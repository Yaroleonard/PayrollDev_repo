from django.contrib import admin
from .models import Department, JobTitle, Employee, SalaryGrade

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager', 'created_at']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'job_title', 'status', 'hire_date']
    list_filter = ['status', 'department', 'employment_type']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']

@admin.register(SalaryGrade)
class SalaryGradeAdmin(admin.ModelAdmin):
    list_display = ['employee', 'basic_salary', 'gross_salary', 'effective_date']

admin.site.register(JobTitle)
