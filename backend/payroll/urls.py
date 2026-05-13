from django.urls import path
from . import views

urlpatterns = [
    # Deductions
    path('deductions/', views.DeductionListCreateView.as_view(), name='deduction_list'),
    path('deductions/<int:pk>/', views.DeductionDetailView.as_view(), name='deduction_detail'),
    path('employees/<int:employee_pk>/deductions/', views.EmployeeDeductionListView.as_view()),

    # Payroll Periods
    path('periods/', views.PayrollPeriodListCreateView.as_view(), name='period_list'),
    path('periods/<int:pk>/', views.PayrollPeriodDetailView.as_view(), name='period_detail'),
    path('periods/<int:pk>/generate/', views.GeneratePayrollView.as_view(), name='generate_payroll'),
    path('periods/<int:pk>/approve/', views.ApprovePayrollView.as_view(), name='approve_payroll'),
    path('periods/<int:pk>/mark-paid/', views.MarkAsPaidView.as_view(), name='mark_paid'),
    path('periods/<int:pk>/summary/', views.PayrollSummaryView.as_view(), name='payroll_summary'),

    # Payslips
    path('payslips/', views.PayslipListView.as_view(), name='payslip_list'),
    path('payslips/<int:pk>/', views.PayslipDetailView.as_view(), name='payslip_detail'),
    path('my-payslips/', views.MyPayslipsView.as_view(), name='my_payslips'),
]
