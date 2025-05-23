from django.urls import path
from . import views
from . import api_views

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
    path('generate/faculty/', views.faculty_report, name='faculty_report'),    path('generate/attendance/', views.attendance_report, name='attendance_report'),
    path('generate/examinations/', views.examination_report, name='examination_report'),
    path('generate/fees/', views.fee_report, name='fee_report'),
    path('generate/library/', views.library_report, name='library_report'),
    path('generate/hostel/', views.hostel_report, name='hostel_report'),
    
    # API Endpoints for Dashboard
    path('api/dashboard/attendance-stats/', api_views.attendance_stats, name='api_attendance_stats'),
    path('api/dashboard/exam-performance/', api_views.exam_performance, name='api_exam_performance'),
    path('api/dashboard/enrollment-stats/', api_views.enrollment_stats, name='api_enrollment_stats'),
    path('api/dashboard/fee-collection-stats/', api_views.fee_collection_stats, name='api_fee_collection_stats'),
    
    # Notification API Endpoints
    path('api/notifications/', api_views.get_notifications, name='api_get_notifications'),
    path('api/notifications/mark-read/', api_views.mark_notification_read, name='api_mark_all_notifications_read'),
    path('api/notifications/mark-read/<int:notification_id>/', api_views.mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/create/', api_views.create_notification, name='api_create_notification'),
    
    # Report Export Endpoints
    path('reports/<int:report_id>/export/', api_views.export_report, name='report_export'),
]
