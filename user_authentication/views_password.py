from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PasswordChangingForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView

@login_required
def change_password(request):
    """View to change password"""
    if request.method == 'POST':
        form = PasswordChangingForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            
            # If this was the user's first login, update the flag
            if hasattr(user, 'profile') and user.profile.is_first_login:
                user.profile.is_first_login = False
                user.profile.save()
            
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
    else:
        form = PasswordChangingForm(request.user)
    
    return render(request, 'user_authentication/change_password.html', {'form': form})

@login_required
def force_password_change(request):
    """View to force password change on first login"""
    # If user has already changed their password, redirect to home
    if not (hasattr(request.user, 'profile') and request.user.profile.is_first_login):
        return redirect('home')
        
    if request.method == 'POST':
        form = PasswordChangingForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            
            # Update the first login flag
            request.user.profile.is_first_login = False
            request.user.profile.save()
            
            messages.success(request, 'Your password has been changed successfully. Welcome!')
            return redirect('home')
    else:
        form = PasswordChangingForm(request.user)
    
    return render(request, 'user_authentication/force_password_change.html', {
        'form': form,
        'is_first_login': True
    })