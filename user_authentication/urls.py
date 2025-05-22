from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.decorators.http import require_POST
from .forms import LoginForm, PasswordChangingForm
from .views_auth import CustomLoginView

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
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='user_authentication/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='user_authentication/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='user_authentication/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='user_authentication/password_reset_complete.html'
    ), name='password_reset_complete'),
]
