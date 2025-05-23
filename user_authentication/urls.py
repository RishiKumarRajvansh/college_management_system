from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.decorators.http import require_POST
from .forms import LoginForm, PasswordChangingForm
from .views_auth import CustomLoginView
from .views_password import force_password_change
from .views_password_reset import request_password_reset, admin_reset_requests, process_reset_request

urlpatterns = [
    # Login view is now handled at the project level
    # Keeping this commented for reference
    # path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='user_authentication/logout.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('change-password/', auth_views.PasswordChangeView.as_view(
        template_name='user_authentication/change_password.html',
        form_class=PasswordChangingForm,
        success_url='/auth/password-changed/'
    ), name='change_password'),
    path('password-changed/', auth_views.PasswordChangeDoneView.as_view(
        template_name='user_authentication/password_changed.html'
    ), name='password_changed'),
    # Custom password reset paths
    path('password-reset/', request_password_reset, name='password_reset'),    path('admin-reset-requests/', admin_reset_requests, name='admin_reset_requests'),
    path('process-reset-request/<uuid:request_id>/', process_reset_request, name='process_reset_request'),
    path('force-password-change/', force_password_change, name='force_password_change'),
]
