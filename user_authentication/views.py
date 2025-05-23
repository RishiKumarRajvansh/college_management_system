from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from .forms import UserRegistrationForm, UserProfileForm, UserUpdateForm
from .models import UserProfile, AuditTrail

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Get the user_type selection
            user_type = form.cleaned_data.get('user_type')
            phone_number = form.cleaned_data.get('phone_number')
            
            # Set Django permissions based on user_type
            if user_type == 'admin':
                user.is_staff = True  # Can access admin site
                user.is_superuser = True  # Has all permissions
            elif user_type == 'faculty':
                user.is_staff = True  # Faculty can access admin site but not superuser
                user.is_superuser = False
            else:  # student
                user.is_staff = False
                user.is_superuser = False
                
            # Save the updated user object
            user.save()            # Create user profile
            UserProfile.objects.create(
                user=user,
                user_type=user_type,
                phone_number=phone_number,
                is_first_login=False  # Self-registered users choose their own password
            )
            
            # Create corresponding records based on user_type
            if user_type == 'student':
                # Import here to avoid circular imports
                from student_management.models import Student
                
                # Create Student record
                Student.objects.create(
                    user=user,
                    name=f"{user.first_name} {user.last_name}".strip(),
                    email=user.email,
                    student_id=f"ST{user.id:06d}"  # Generate a student ID based on user ID
                )
            elif user_type == 'faculty':
                # Import here to avoid circular imports
                from faculty_management.models import Faculty
                
                # Create Faculty record
                Faculty.objects.create(
                    user=user,
                    name=f"{user.first_name} {user.last_name}".strip(),
                    email=user.email,
                    faculty_id=f"FA{user.id:06d}"  # Generate a faculty ID based on user ID
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
            messages.success(request, f'Account created for {user.username} as {user_type}. You can now log in.')
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
