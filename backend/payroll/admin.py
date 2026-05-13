from django.contrib import admin
from .models import Deduction, PayrollPeriod, Payslip, TaxBracket

admin.site.register(TaxBracket)
admin.site.register(Deduction)

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'status', 'payment_date', 'created_by']
    list_filter = ['status', 'year']

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_period', 'gross_salary', 'net_salary', 'is_paid']
    list_filter = ['is_paid', 'payroll_period']
