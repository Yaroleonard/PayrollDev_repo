from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsHRManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_hr_manager


class IsPayrollOfficer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_payroll_officer


class IsOwnerOrHRManager(BasePermission):
    """Allow employees to view their own data; HR+ can view all."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_hr_manager:
            return True
        # Check if obj has employee or user link
        if hasattr(obj, 'employee'):
            return obj.employee.user == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return False
