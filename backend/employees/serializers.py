from rest_framework import serializers
from .models import Department, JobTitle, Employee, SalaryGrade
from authentication.serializers import UserSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'manager', 'employee_count', 'created_at']

    def get_employee_count(self, obj):
        return obj.employees.filter(status='active').count()


class JobTitleSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = JobTitle
        fields = ['id', 'title', 'department', 'department_name', 'min_salary', 'max_salary']


class SalaryGradeSerializer(serializers.ModelSerializer):
    gross_salary = serializers.ReadOnlyField()

    class Meta:
        model = SalaryGrade
        fields = [
            'id', 'basic_salary', 'housing_allowance', 'transport_allowance',
            'medical_allowance', 'other_allowances', 'gross_salary', 'effective_date',
            'created_at', 'updated_at'
        ]


class EmployeeListSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    job_title_name = serializers.CharField(source='job_title.title', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'email', 'department_name',
            'job_title_name', 'employment_type', 'status', 'hire_date'
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    salary_grade = SalaryGradeSerializer(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    job_title_name = serializers.CharField(source='job_title.title', read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Employee
        fields = '__all__'


class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        exclude = ['employee_id', 'created_at', 'updated_at']
