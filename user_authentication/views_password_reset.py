from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from .forms import PasswordResetRequestForm, AdminPasswordResetForm
from .models import PasswordResetRequest, AuditTrail

def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        return (hasattr(user, 'profile') and user.profile.user_type == 'admin') or user.is_superuser
    except:
        return False

def request_password_reset(request):
    """View to handle password reset requests from users"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username']
            
            # Find the user
            user = User.objects.filter(username=username_or_email).first()
            if not user:
                user = User.objects.filter(email=username_or_email).first()
            
            # Check if there's already a pending request
            existing_request = PasswordResetRequest.objects.filter(
                user=user,
                status='pending'
            ).exists()
            
            if existing_request:
                messages.warning(request, 
                    "You already have a pending password reset request. "
                    "Please wait for an administrator to process it."
                )
            else:
                # Create a new password reset request
                reset_request = PasswordResetRequest.objects.create(user=user)
                
                # Create audit trail
                AuditTrail.objects.create(
                    user=user,
                    action='create',
                    module='password_reset',
                    description=f"Password reset requested for {user.username}",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                messages.success(request, 
                    "Your password reset request has been submitted. "
                    "An administrator will process your request and provide you "
                    "with a new temporary password. Please check with the admin."
                )
            
            return redirect('login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'user_authentication/password_reset_request.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_reset_requests(request):
    """View for admins to see the list of password reset requests"""
    requests = PasswordResetRequest.objects.all().order_by('-requested_at')
    
    return render(request, 'user_authentication/admin_reset_requests.html', {'requests': requests})

@login_required
@user_passes_test(is_admin)
def process_reset_request(request, request_id):
    """View for admins to process a password reset request"""
    reset_request = get_object_or_404(PasswordResetRequest, request_id=request_id)
    
    if reset_request.status != 'pending':
        messages.warning(request, f"This request has already been {reset_request.status}.")
        return redirect('admin_reset_requests')
    
    if request.method == 'POST':
        form = AdminPasswordResetForm(request.POST, instance=reset_request)
        if form.is_valid():
            # Save the reset request
            reset_request = form.save(commit=False)
            reset_request.processed_by = request.user
            reset_request.processed_at = timezone.now()
            
            if reset_request.status == 'processed':
                # Update the user's password
                user = reset_request.user
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                
                # Set first login flag to true so user will be forced to change password
                if hasattr(user, 'profile'):
                    user.profile.is_first_login = True
                    user.profile.save()
                
                # Create audit trail
                AuditTrail.objects.create(
                    user=request.user,
                    action='update',
                    module='password_reset',
                    record_id=user.id,
                    description=f"Password reset processed for {user.username} by {request.user.username}",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                messages.success(request, 
                    f"Password reset completed for {user.username}. "
                    f"The new temporary password is: {form.cleaned_data['new_password']}"
                )
            else:
                # Create audit trail for rejected request
                AuditTrail.objects.create(
                    user=request.user,
                    action='update',
                    module='password_reset',
                    record_id=reset_request.user.id,
                    description=f"Password reset rejected for {reset_request.user.username} by {request.user.username}",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                messages.info(request, f"Password reset request for {reset_request.user.username} has been rejected.")
            
            # Save the reset request after audit trail creation
            reset_request.save()
            
            return redirect('admin_reset_requests')
    else:
        form = AdminPasswordResetForm(instance=reset_request)
    
    context = {
        'form': form,
        'reset_request': reset_request
    }
    
    return render(request, 'user_authentication/process_reset_request.html', context)
