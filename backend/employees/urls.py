from django.urls import path
from . import views

urlpatterns = [
    path('', views.EmployeeListCreateView.as_view(), name='employee_list'),
    path('me/', views.MyProfileView.as_view(), name='my_profile'),
    path('stats/', views.EmployeeStatsView.as_view(), name='employee_stats'),
    path('<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('<int:employee_pk>/salary/', views.SalaryGradeView.as_view(), name='salary_grade'),
    path('departments/', views.DepartmentListCreateView.as_view(), name='department_list'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('job-titles/', views.JobTitleListCreateView.as_view(), name='job_title_list'),
    path('job-titles/<int:pk>/', views.JobTitleDetailView.as_view(), name='job_title_detail'),
]
