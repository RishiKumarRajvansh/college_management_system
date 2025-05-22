from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileForm, UserUpdateForm
from .models import UserProfile, AuditTrail

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            user_type = form.cleaned_data.get('user_type')
            phone_number = form.cleaned_data.get('phone_number')
            UserProfile.objects.create(
                user=user,
                user_type=user_type,
                phone_number=phone_number
            )
            
            # Create audit trail
            AuditTrail.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action='create',
                module='user',
                record_id=user.id,
                description=f'New user {user.username} registered as {user_type}',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            # Display success message
            messages.success(request, f'Account created for {user.username}. You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'user_authentication/register.html', {'form': form})

@login_required
def profile(request):
    # Get recent activities
    activities = AuditTrail.objects.filter(user=request.user).order_by('-action_time')[:10]
    
    # Create a new audit trail entry for viewing profile
    AuditTrail.objects.create(
        user=request.user,
        action='view',
        module='profile',
        description=f'User {request.user.username} viewed their profile',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )
    
    context = {
        'user': request.user,
        'activities': activities
    }
    return render(request, 'user_authentication/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            
            # Create audit trail
            AuditTrail.objects.create(
                user=request.user,
                action='update',
                module='profile',
                record_id=request.user.id,
                description=f'User {request.user.username} updated their profile',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'user_authentication/edit_profile.html', context)
