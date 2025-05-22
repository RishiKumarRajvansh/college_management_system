from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Student
from .forms import StudentForm, StudentSearchForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from user_authentication.models import UserProfile  # Added import

# Helper function to check if user is admin
def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        # Check if user has a profile and if its type is 'admin', or if the user is a superuser
        return (hasattr(user, 'profile') and user.profile.user_type == 'admin') or user.is_superuser
    except UserProfile.DoesNotExist:  # Catching the specific exception if profile does not exist
        return False

@login_required
def student_list(request):
    """View to list all students with search and filter options"""
    students = Student.objects.all()
    form = StudentSearchForm(request.GET)
    
    # Apply filters if the form is valid
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        course_filter = form.cleaned_data.get('course')
        year_filter = form.cleaned_data.get('year')
        
        if search_query:
            students = students.filter(
                Q(name__icontains=search_query) | 
                Q(email__icontains=search_query) | 
                Q(student_id__icontains=search_query)
            )
        
        if course_filter:
            students = students.filter(course=course_filter)
            
        if year_filter and year_filter != '0':  # '0' is 'All Years'
            students = students.filter(year=year_filter)
      # Order students by ID to avoid UnorderedObjectListWarning
    students = students.order_by('student_id')
    
    # Paginate the results
    paginator = Paginator(students, 10)  # Show 10 students per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_students': students.count(),
    }
    
    return render(request, 'student_management/student_list.html', context)

@login_required
@user_passes_test(is_admin)
def student_create(request):
    """View to create a new student"""
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            # Create user account
            username = form.cleaned_data['email']
            # Generate password as student_id + first 3 chars of name
            # This is just initial - student will be asked to change on first login
            password = f"student{form.cleaned_data['name'][:3].lower()}"
            
            user = User.objects.create_user(
                username=username,
                email=form.cleaned_data['email'],
                password=password,
                first_name=form.cleaned_data['name'].split()[0],
                last_name=' '.join(form.cleaned_data['name'].split()[1:]) if len(form.cleaned_data['name'].split()) > 1 else '',
            )
            
            # Create student profile
            student = form.save(commit=False)
            student.user = user
            student.save()
            
            messages.success(request, f'Student {student.name} created successfully!')
            return redirect('student_detail', pk=student.student_id)
    else:
        form = StudentForm()
    
    return render(request, 'student_management/student_form.html', {'form': form, 'title': 'Add Student'})

@login_required
def student_detail(request, pk):
    """View to display student details"""
    student = get_object_or_404(Student, student_id=pk)
    
    # Only allow access if admin or the student themselves
    if not is_admin(request.user) and request.user != student.user:
        messages.error(request, "You don't have permission to view this student's details")
        return redirect('student_list')
        
    return render(request, 'student_management/student_detail.html', {'student': student})

@login_required
@user_passes_test(is_admin)
def student_update(request, pk):
    """View to update student information"""
    student = get_object_or_404(Student, student_id=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            # Update user information as well
            student.user.email = form.cleaned_data['email']
            student.user.first_name = form.cleaned_data['name'].split()[0]
            student.user.last_name = ' '.join(form.cleaned_data['name'].split()[1:]) if len(form.cleaned_data['name'].split()) > 1 else ''
            student.user.save()
            
            form.save()
            messages.success(request, f'Student {student.name} updated successfully!')
            return redirect('student_detail', pk=student.student_id)
    else:
        form = StudentForm(instance=student)
    
    return render(request, 'student_management/student_form.html', {
        'form': form, 
        'title': 'Update Student',
        'student': student
    })

@login_required
@user_passes_test(is_admin)
def student_delete(request, pk):
    """View to delete a student"""
    student = get_object_or_404(Student, student_id=pk)
    
    if request.method == 'POST':
        user = student.user
        student_name = student.name
        student.delete()
        # Delete associated user account
        user.delete()
        messages.success(request, f'Student {student_name} deleted successfully!')
        return redirect('student_list')
        
    return render(request, 'student_management/student_confirm_delete.html', {'student': student})
