from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import LeaveType, LeaveRequest, LeaveBalance
from .serializers import (
    LeaveTypeSerializer, LeaveRequestSerializer,
    LeaveRequestCreateSerializer, LeaveApprovalSerializer, LeaveBalanceSerializer
)
from authentication.permissions import IsHRManager


class LeaveTypeListCreateView(generics.ListCreateAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsHRManager()]
        return [IsAuthenticated()]


class LeaveTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsHRManager]


class LeaveRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = LeaveRequest.objects.select_related('employee__user', 'leave_type', 'reviewed_by')

        if user.is_hr_manager:
            status_filter = self.request.query_params.get('status')
            employee_id = self.request.query_params.get('employee_id')
            if status_filter:
                qs = qs.filter(status=status_filter)
            if employee_id:
                qs = qs.filter(employee_id=employee_id)
            return qs

        return qs.filter(employee__user=user)

    def get_serializer_class(self):
        return LeaveRequestCreateSerializer if self.request.method == 'POST' else LeaveRequestSerializer


class LeaveRequestDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_hr_manager:
            return LeaveRequest.objects.all()
        return LeaveRequest.objects.filter(employee__user=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'pending':
            return Response({'error': 'Only pending requests can be cancelled.'}, status=400)
        instance.status = 'cancelled'
        instance.save()
        return Response({'detail': 'Leave request cancelled.'})


class ApproveLeaveView(APIView):
    permission_classes = [IsHRManager]

    def post(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk)
        serializer = LeaveApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = serializer.validated_data['action']
        comments = serializer.validated_data.get('comments', '')

        if leave.status != 'pending':
            return Response({'error': 'Only pending requests can be reviewed.'}, status=400)

        leave.status = 'approved' if action == 'approve' else 'rejected'
        leave.reviewed_by = request.user
        leave.reviewer_comments = comments
        leave.reviewed_at = timezone.now()
        leave.save()

        # Update leave balance if approved
        if leave.status == 'approved':
            year = leave.start_date.year
            balance, _ = LeaveBalance.objects.get_or_create(
                employee=leave.employee,
                leave_type=leave.leave_type,
                year=year,
                defaults={'total_days': leave.leave_type.days_allowed}
            )
            balance.used_days += leave.duration_days
            balance.save()

        return Response({
            'detail': f'Leave request {leave.status}.',
            'leave': LeaveRequestSerializer(leave).data,
        })


class LeaveBalanceListView(generics.ListAPIView):
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        year = self.request.query_params.get('year', timezone.now().year)
        qs = LeaveBalance.objects.select_related('employee__user', 'leave_type').filter(year=year)

        if not user.is_hr_manager:
            qs = qs.filter(employee__user=user)
        return qs


class MyLeaveBalanceView(generics.ListAPIView):
    serializer_class = LeaveBalanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        year = self.request.query_params.get('year', timezone.now().year)
        return LeaveBalance.objects.filter(
            employee__user=self.request.user, year=year
        ).select_related('leave_type')
