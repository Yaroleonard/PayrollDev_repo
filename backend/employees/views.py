from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from .models import Department, JobTitle, Employee, SalaryGrade
from .serializers import (
    DepartmentSerializer, JobTitleSerializer, EmployeeListSerializer,
    EmployeeDetailSerializer, EmployeeCreateSerializer, SalaryGradeSerializer
)
from authentication.permissions import IsHRManager, IsPayrollOfficer, IsOwnerOrHRManager


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsHRManager()]
        return [IsAuthenticated()]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsHRManager]


class JobTitleListCreateView(generics.ListCreateAPIView):
    queryset = JobTitle.objects.select_related('department').all()
    serializer_class = JobTitleSerializer
    permission_classes = [IsAuthenticated]


class JobTitleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer
    permission_classes = [IsHRManager]


class EmployeeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsHRManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'user__email']
    ordering_fields = ['hire_date', 'user__first_name', 'department__name']
    ordering = ['user__first_name']

    def get_queryset(self):
        qs = Employee.objects.select_related('user', 'department', 'job_title')
        status_filter = self.request.query_params.get('status')
        department = self.request.query_params.get('department')
        if status_filter:
            qs = qs.filter(status=status_filter)
        if department:
            qs = qs.filter(department_id=department)
        return qs

    def get_serializer_class(self):
        return EmployeeCreateSerializer if self.request.method == 'POST' else EmployeeListSerializer


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.select_related('user', 'department', 'job_title', 'salary_grade')
    permission_classes = [IsAuthenticated, IsOwnerOrHRManager]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeCreateSerializer
        return EmployeeDetailSerializer


class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = EmployeeDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.employee_profile


class SalaryGradeView(generics.RetrieveUpdateAPIView):
    serializer_class = SalaryGradeSerializer
    permission_classes = [IsPayrollOfficer]

    def get_object(self):
        employee_id = self.kwargs['employee_pk']
        employee = Employee.objects.get(pk=employee_id)
        grade, _ = SalaryGrade.objects.get_or_create(
            employee=employee,
            defaults={'basic_salary': 0, 'effective_date': '2024-01-01'}
        )
        return grade


class EmployeeStatsView(APIView):
    permission_classes = [IsHRManager]

    def get(self, request):
        total = Employee.objects.count()
        active = Employee.objects.filter(status='active').count()
        by_dept = list(
            Department.objects.annotate(count=Count('employees')).values('name', 'count')
        )
        by_type = {}
        for emp_type, _ in Employee.EMPLOYMENT_TYPE:
            by_type[emp_type] = Employee.objects.filter(employment_type=emp_type, status='active').count()

        return Response({
            'total_employees': total,
            'active_employees': active,
            'inactive_employees': total - active,
            'by_department': by_dept,
            'by_employment_type': by_type,
        })
