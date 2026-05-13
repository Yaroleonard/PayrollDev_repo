from django.urls import path
from . import views

urlpatterns = [
    path('types/', views.LeaveTypeListCreateView.as_view(), name='leave_type_list'),
    path('types/<int:pk>/', views.LeaveTypeDetailView.as_view(), name='leave_type_detail'),
    path('requests/', views.LeaveRequestListCreateView.as_view(), name='leave_request_list'),
    path('requests/<int:pk>/', views.LeaveRequestDetailView.as_view(), name='leave_request_detail'),
    path('requests/<int:pk>/review/', views.ApproveLeaveView.as_view(), name='approve_leave'),
    path('balances/', views.LeaveBalanceListView.as_view(), name='leave_balance_list'),
    path('my-balances/', views.MyLeaveBalanceView.as_view(), name='my_leave_balance'),
]
