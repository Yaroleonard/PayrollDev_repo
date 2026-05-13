from django.db import models
from authentication.models import User
import uuid


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        'Employee', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='managed_department'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.name


class JobTitle(models.Model):
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='job_titles')
    min_salary = models.DecimalField(max_digits=12, decimal_places=2)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'job_titles'

    def __str__(self):
        return f"{self.title} ({self.department.name})"


class Employee(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]
    EMPLOYMENT_TYPE = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
    ]

    employee_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True, related_name='employees')

    # Personal Info
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    national_id = models.CharField(max_length=50, blank=True, unique=True)
    profile_picture = models.ImageField(upload_to='employees/photos/', blank=True, null=True)

    # Employment Info
    hire_date = models.DateField()
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE, default='full_time')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    termination_date = models.DateField(null=True, blank=True)

    # Bank Details
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        ordering = ['user__first_name', 'user__last_name']

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last = Employee.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.employee_id = f"EMP{next_id:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email


class SalaryGrade(models.Model):
    """Defines salary structure per employee"""
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='salary_grade')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    housing_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    effective_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'salary_grades'

    @property
    def gross_salary(self):
        return (
            self.basic_salary + self.housing_allowance +
            self.transport_allowance + self.medical_allowance +
            self.other_allowances
        )

    def __str__(self):
        return f"{self.employee.full_name} - GHS {self.gross_salary}"
