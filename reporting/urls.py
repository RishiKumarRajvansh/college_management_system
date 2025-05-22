from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='reporting_dashboard'),
    
    # Report List and Management
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/<int:report_id>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('reports/<int:report_id>/delete/', views.ReportDeleteView.as_view(), name='report_delete'),
    
    # Report Generation Options
    path('generate/', views.generate_report_options, name='generate_report_options'),
    
    # Report Generation by Module
    path('generate/students/', views.student_report, name='student_report'),
    path('generate/faculty/', views.faculty_report, name='faculty_report'),
    path('generate/attendance/', views.attendance_report, name='attendance_report'),
    path('generate/examinations/', views.examination_report, name='examination_report'),
    path('generate/fees/', views.fee_report, name='fee_report'),
    path('generate/library/', views.library_report, name='library_report'),
    path('generate/hostel/', views.hostel_report, name='hostel_report'),
]
