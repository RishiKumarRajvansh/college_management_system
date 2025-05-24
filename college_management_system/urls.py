"""
URL configuration for college_management_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home_view, admin_dashboard, system_activity_logs
from django.contrib.auth import views as auth_views
from user_authentication.forms import LoginForm
from user_authentication.views_auth import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),    path('', home_view, name='home'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('system-logs/', system_activity_logs, name='system_activity_logs'),
    path('auth/', include('user_authentication.urls', namespace='auth')),
    # Add login URL at project level with our custom view
    path('login/', CustomLoginView.as_view(), name='login'),
    path('students/', include('student_management.urls')),
    path('faculty/', include('faculty_management.urls')),
    path('courses/', include('course_management.urls')),
    path('attendance/', include('attendance_management.urls')),
    path('examinations/', include('examination.urls')),
    path('library/', include('library_management.urls')),
    path('hostel/', include('hostel_management.urls')),
    path('fees/', include('fee_management.urls')),
    path('reports/', include('reporting.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
