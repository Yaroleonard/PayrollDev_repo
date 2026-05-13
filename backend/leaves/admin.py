from django.contrib import admin
from .models import LeaveType, LeaveRequest, LeaveBalance

admin.site.register(LeaveType)

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'leave_type']

admin.site.register(LeaveBalance)
