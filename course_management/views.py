from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Course
from .forms import CourseForm, CourseSearchForm
from user_authentication.models import UserProfile  # Added import

# Helper function to check if user is admin
def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        return (hasattr(user, 'profile') and user.profile.user_type == 'admin') or user.is_superuser
    except UserProfile.DoesNotExist:
        return False

@login_required
def course_list(request):
    """View to list all courses with search and filter options"""
    courses = Course.objects.all()
    form = CourseSearchForm(request.GET)
    
    # Apply filters if the form is valid
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        faculty_filter = form.cleaned_data.get('faculty')
        credits_filter = form.cleaned_data.get('credits')
        
        if search_query:
            courses = courses.filter(
                Q(course_name__icontains=search_query) | 
                Q(course_id__icontains=search_query)
            )
        
        if faculty_filter:
            courses = courses.filter(faculty=faculty_filter)
            
        if credits_filter and credits_filter != '0':  # '0' is 'All Credits'
            courses = courses.filter(credits=credits_filter)
      # Order courses by ID to avoid UnorderedObjectListWarning
    courses = courses.order_by('course_id')
    
    # Paginate the results
    paginator = Paginator(courses, 10)  # Show 10 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_courses': courses.count(),
    }
    
    return render(request, 'course_management/course_list.html', context)

@login_required
@user_passes_test(is_admin)
def course_create(request):
    """View to create a new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course {course.course_name} created successfully!')
            return redirect('course_detail', pk=course.course_id)
    else:
        form = CourseForm()
    
    return render(request, 'course_management/course_form.html', {'form': form, 'title': 'Add Course'})

@login_required
def course_detail(request, pk):
    """View to display course details"""
    course = get_object_or_404(Course, course_id=pk)
    
    # Get students enrolled in this course (if applicable)
    students = course.student_set.all()
    
    context = {
        'course': course,
        'students': students,
    }
        
    return render(request, 'course_management/course_detail.html', context)

@login_required
@user_passes_test(is_admin)
def course_update(request, pk):
    """View to update course information"""
    course = get_object_or_404(Course, course_id=pk)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course {course.course_name} updated successfully!')
            return redirect('course_detail', pk=course.course_id)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'course_management/course_form.html', {'form': form, 'title': 'Update Course'})

@login_required
@user_passes_test(is_admin)
def course_delete(request, pk):
    """View to delete a course"""
    course = get_object_or_404(Course, course_id=pk)
    
    if request.method == 'POST':
        course_name = course.course_name
        course.delete()
        messages.success(request, f'Course {course_name} deleted successfully!')
        return redirect('course_list')
        
    return render(request, 'course_management/course_confirm_delete.html', {'course': course})
