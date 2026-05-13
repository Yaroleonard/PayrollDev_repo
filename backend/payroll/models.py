from django.db import models
from decimal import Decimal
from employees.models import Employee


class TaxBracket(models.Model):
    """Ghana PAYE tax brackets"""
    min_income = models.DecimalField(max_digits=12, decimal_places=2)
    max_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Tax rate as percentage")
    description = models.CharField(max_length=100)

    class Meta:
        db_table = 'tax_brackets'
        ordering = ['min_income']

    def __str__(self):
        return f"{self.description}: {self.rate}%"


class Deduction(models.Model):
    """Configurable deduction types (SSNIT, loan, etc.)"""
    DEDUCTION_TYPES = [
        ('percentage', 'Percentage of Basic'),
        ('fixed', 'Fixed Amount'),
    ]
    name = models.CharField(max_length=100)
    deduction_type = models.CharField(max_length=20, choices=DEDUCTION_TYPES)
    value = models.DecimalField(max_digits=8, decimal_places=2, help_text="Amount or percentage")
    is_mandatory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'deductions'

    def __str__(self):
        return self.name


class EmployeeDeduction(models.Model):
    """Deductions assigned to specific employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='deductions')
    deduction = models.ForeignKey(Deduction, on_delete=models.CASCADE)
    custom_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'employee_deductions'

    def __str__(self):
        return f"{self.employee.full_name} - {self.deduction.name}"


class PayrollPeriod(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
    ]

    month = models.IntegerField()
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL,
        null=True, related_name='created_payrolls'
    )
    approved_by = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_payrolls'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payroll_periods'
        unique_together = ['month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"Payroll {self.month:02d}/{self.year}"


class Payslip(models.Model):
    """Individual payslip per employee per period"""
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payslips')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payslips')

    # Earnings
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=12, decimal_places=2)

    # Deductions
    paye_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ssnit_employee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ssnit_employer = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2)

    # Net Pay
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)

    # Deduction breakdown (JSON)
    deductions_breakdown = models.JSONField(default=dict)

    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payslips'
        unique_together = ['payroll_period', 'employee']
        ordering = ['-payroll_period__year', '-payroll_period__month']

    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_period}"
