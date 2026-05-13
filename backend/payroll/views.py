from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from decimal import Decimal

from .models import Deduction, EmployeeDeduction, PayrollPeriod, Payslip
from .serializers import (
    DeductionSerializer, EmployeeDeductionSerializer,
    PayrollPeriodSerializer, PayrollPeriodCreateSerializer, PayslipSerializer
)
from .tax_calculator import compute_payslip
from employees.models import Employee
from authentication.permissions import IsPayrollOfficer, IsHRManager, IsOwnerOrHRManager


class DeductionListCreateView(generics.ListCreateAPIView):
    queryset = Deduction.objects.filter(is_active=True)
    serializer_class = DeductionSerializer
    permission_classes = [IsPayrollOfficer]


class DeductionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deduction.objects.all()
    serializer_class = DeductionSerializer
    permission_classes = [IsPayrollOfficer]


class EmployeeDeductionListView(generics.ListCreateAPIView):
    serializer_class = EmployeeDeductionSerializer
    permission_classes = [IsPayrollOfficer]

    def get_queryset(self):
        return EmployeeDeduction.objects.filter(
            employee_id=self.kwargs['employee_pk'],
            is_active=True
        ).select_related('deduction')


class PayrollPeriodListCreateView(generics.ListCreateAPIView):
    queryset = PayrollPeriod.objects.all()
    permission_classes = [IsPayrollOfficer]

    def get_serializer_class(self):
        return PayrollPeriodCreateSerializer if self.request.method == 'POST' else PayrollPeriodSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PayrollPeriodDetailView(generics.RetrieveUpdateAPIView):
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    permission_classes = [IsPayrollOfficer]


class GeneratePayrollView(APIView):
    """Generate payslips for all active employees in a payroll period."""
    permission_classes = [IsPayrollOfficer]

    def post(self, request, pk):
        period = get_object_or_404(PayrollPeriod, pk=pk)

        if period.status not in ['draft', 'processing']:
            return Response(
                {'error': 'Payroll can only be generated for draft or processing periods.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        period.status = 'processing'
        period.save()

        employees = Employee.objects.filter(
            status='active'
        ).select_related('salary_grade').prefetch_related('deductions__deduction')

        created, updated, errors = 0, 0, []

        for employee in employees:
            if not hasattr(employee, 'salary_grade'):
                errors.append(f"{employee.full_name}: No salary grade configured.")
                continue

            extra_deductions = employee.deductions.filter(is_active=True)
            bonus = Decimal(request.data.get('bonuses', {}).get(str(employee.id), '0'))
            overtime = Decimal(request.data.get('overtime', {}).get(str(employee.id), '0'))

            data = compute_payslip(employee.salary_grade, extra_deductions, bonus, overtime)

            payslip, is_new = Payslip.objects.update_or_create(
                payroll_period=period,
                employee=employee,
                defaults=data
            )
            if is_new:
                created += 1
            else:
                updated += 1

        return Response({
            'period': str(period),
            'payslips_created': created,
            'payslips_updated': updated,
            'errors': errors,
            'status': period.status,
        })


class ApprovePayrollView(APIView):
    permission_classes = [IsHRManager]

    def post(self, request, pk):
        period = get_object_or_404(PayrollPeriod, pk=pk)
        if period.status != 'processing':
            return Response({'error': 'Only processing payrolls can be approved.'}, status=400)
        period.status = 'approved'
        period.approved_by = request.user
        period.save()
        return Response({'detail': f'Payroll {period} approved successfully.'})


class MarkAsPaidView(APIView):
    permission_classes = [IsHRManager]

    def post(self, request, pk):
        from django.utils import timezone
        period = get_object_or_404(PayrollPeriod, pk=pk)
        if period.status != 'approved':
            return Response({'error': 'Only approved payrolls can be marked as paid.'}, status=400)
        period.status = 'paid'
        period.save()
        period.payslips.update(is_paid=True, paid_at=timezone.now())
        return Response({'detail': f'Payroll {period} marked as paid.'})


class PayslipListView(generics.ListAPIView):
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Payslip.objects.select_related('employee__user', 'payroll_period')

        if user.is_payroll_officer:
            employee_id = self.request.query_params.get('employee_id')
            period_id = self.request.query_params.get('period_id')
            if employee_id:
                qs = qs.filter(employee_id=employee_id)
            if period_id:
                qs = qs.filter(payroll_period_id=period_id)
            return qs

        # Regular employees only see their own
        return qs.filter(employee__user=user)


class MyPayslipsView(generics.ListAPIView):
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payslip.objects.filter(
            employee__user=self.request.user
        ).select_related('payroll_period').order_by('-payroll_period__year', '-payroll_period__month')


class PayslipDetailView(generics.RetrieveAPIView):
    serializer_class = PayslipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_payroll_officer:
            return Payslip.objects.all()
        return Payslip.objects.filter(employee__user=user)


class PayrollSummaryView(APIView):
    permission_classes = [IsPayrollOfficer]

    def get(self, request, pk):
        period = get_object_or_404(PayrollPeriod, pk=pk)
        from django.db.models import Sum, Count
        stats = period.payslips.aggregate(
            total_gross=Sum('gross_salary'),
            total_net=Sum('net_salary'),
            total_paye=Sum('paye_tax'),
            total_ssnit_emp=Sum('ssnit_employee'),
            total_ssnit_er=Sum('ssnit_employer'),
            total_deductions=Sum('total_deductions'),
            count=Count('id'),
        )
        return Response({
            'period': PayrollPeriodSerializer(period).data,
            'summary': stats,
        })
