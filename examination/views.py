from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.http import HttpResponse
from datetime import datetime, timedelta
from user_authentication.models import UserProfile
from .models import Examination, Result
from .forms import (
    ExaminationForm, ResultForm, BulkResultForm, 
    ExaminationSearchForm, ResultSearchForm
)
from student_management.models import Student

# Helper function to check if user is admin or faculty
def is_admin_or_faculty(user):
    if not user.is_authenticated:
        return False
    try:
        # Check if user has a profile and if its type is 'admin' or 'faculty', or if the user is a superuser
        return (hasattr(user, 'profile') and user.profile.user_type in ['admin', 'faculty']) or user.is_superuser
    except UserProfile.DoesNotExist:
        return False

# Helper function to check if user is admin
def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        return (hasattr(user, 'profile') and user.profile.user_type == 'admin') or user.is_superuser
    except UserProfile.DoesNotExist:
        return False

@login_required
def examination_list(request):
    """View to list all examinations with search and filter options"""
    examinations = Examination.objects.all().order_by('-date')
    form = ExaminationSearchForm(request.GET)
    
    # Apply filters if the form is valid
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        exam_type = form.cleaned_data.get('exam_type')
        course = form.cleaned_data.get('course')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        
        if search_query:
            examinations = examinations.filter(
                Q(exam_name__icontains=search_query) |
                Q(exam_id__icontains=search_query)
            )
        
        if exam_type:
            examinations = examinations.filter(exam_type=exam_type)
        
        if course:
            examinations = examinations.filter(course=course)
            
        if start_date:
            examinations = examinations.filter(date__date__gte=start_date)
            
        if end_date:
            examinations = examinations.filter(date__date__lte=end_date)
    
    # Paginate the results
    paginator = Paginator(examinations, 10)  # Show 10 examinations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    
    return render(request, 'examination/examination_list.html', context)

@login_required
@user_passes_test(is_admin_or_faculty)
def examination_create(request):
    """View to create a new examination"""
    if request.method == 'POST':
        form = ExaminationForm(request.POST)
        if form.is_valid():
            examination = form.save()
            messages.success(request, f'Examination "{examination.exam_name}" created successfully.')
            return redirect('examination_list')
    else:
        form = ExaminationForm()
    
    context = {
        'form': form,
        'title': 'Create Examination',
    }
    
    return render(request, 'examination/examination_form.html', context)

@login_required
def examination_detail(request, pk):
    """View to display examination details"""
    examination = get_object_or_404(Examination, pk=pk)
    results = Result.objects.filter(examination=examination)
    
    context = {
        'examination': examination,
        'results': results,
    }
    
    return render(request, 'examination/examination_detail.html', context)

@login_required
@user_passes_test(is_admin_or_faculty)
def examination_update(request, pk):
    """View to update an existing examination"""
    examination = get_object_or_404(Examination, pk=pk)
    
    if request.method == 'POST':
        form = ExaminationForm(request.POST, instance=examination)
        if form.is_valid():
            form.save()
            messages.success(request, f'Examination "{examination.exam_name}" updated successfully.')
            return redirect('examination_detail', pk=pk)
    else:
        form = ExaminationForm(instance=examination)
    
    context = {
        'form': form,
        'title': 'Update Examination',
        'examination': examination,
    }
    
    return render(request, 'examination/examination_form.html', context)

@login_required
@user_passes_test(is_admin_or_faculty)
def examination_delete(request, pk):
    """View to delete an examination"""
    examination = get_object_or_404(Examination, pk=pk)
    
    if request.method == 'POST':
        examination_name = examination.exam_name
        examination.delete()
        messages.success(request, f'Examination "{examination_name}" deleted successfully.')
        return redirect('examination_list')
    
    context = {
        # The confirmation template needs the named object to build exam_id URLs.
        'examination': examination,
        'has_results': examination.results.exists(),
        'title': 'Delete Examination',
    }
    
    return render(request, 'examination/examination_confirm_delete.html', context)

@login_required
def result_list(request):
    """View to list all results with search and filter options"""
    results = Result.objects.all().order_by('-examination__date', 'student__name')
    form = ResultSearchForm(request.GET)
    
    # Apply filters if the form is valid
    if form.is_valid():
        student = form.cleaned_data.get('student')
        examination = form.cleaned_data.get('examination')
        status = form.cleaned_data.get('status')
        grade = form.cleaned_data.get('grade')
        
        if student:
            results = results.filter(student=student)
        
        if examination:
            results = results.filter(examination=examination)
        
        if status:
            results = results.filter(status=status)
            
        if grade:
            results = results.filter(grade=grade)
    
    # Paginate the results
    paginator = Paginator(results, 15)  # Show 15 results per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    
    return render(request, 'examination/result_list.html', context)

@login_required
@user_passes_test(is_admin_or_faculty)
def result_create(request, examination_id=None):
    """View to create a new result"""
    initial_data = {}
    if examination_id:
        examination = get_object_or_404(Examination, pk=examination_id)
        initial_data['examination'] = examination
    
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            
            # Calculate percentage
            if result.examination.total_marks > 0:
                result.percentage = (result.marks_obtained / result.examination.total_marks) * 100
            
            # Determine grade and status
            if result.marks_obtained >= result.examination.passing_marks:
                if result.percentage >= 90:
                    result.grade = 'A+'
                elif result.percentage >= 80:
                    result.grade = 'A'
                elif result.percentage >= 70:
                    result.grade = 'B+'
                elif result.percentage >= 60:
                    result.grade = 'B'
                elif result.percentage >= 50:
                    result.grade = 'C+'
                elif result.percentage >= 40:
                    result.grade = 'C'
                else:
                    result.grade = 'D'
                
                result.status = 'pass'
            else:
                result.grade = 'F'
                result.status = 'fail'
            
            result.save()
            messages.success(request, f'Result for {result.student.name} created successfully.')
            return redirect('result_list')
    else:
        form = ResultForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Create Result',
        'examination_id': examination_id,
    }
    
    return render(request, 'examination/result_form.html', context)

@login_required
def result_detail(request, pk):
    """View to display result details"""
    result = get_object_or_404(Result, pk=pk)
    
    context = {
        'result': result,
    }
    
    return render(request, 'examination/result_detail.html', context)

@login_required
@user_passes_test(is_admin_or_faculty)
def result_update(request, pk):
    """View to update an existing result"""
    result = get_object_or_404(Result, pk=pk)
    
    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            result = form.save(commit=False)
            
            # Recalculate percentage
            if result.examination.total_marks > 0:
                result.percentage = (result.marks_obtained / result.examination.total_marks) * 100
            
            # Re-determine grade and status
            if result.marks_obtained >= result.examination.passing_marks:
                if result.percentage >= 90:
                    result.grade = 'A+'
                elif result.percentage >= 80:
                    result.grade = 'A'
                elif result.percentage >= 70:
                    result.grade = 'B+'
                elif result.percentage >= 60:
                    result.grade = 'B'
                elif result.percentage >= 50:
                    result.grade = 'C+'
                elif result.percentage >= 40:
                    result.grade = 'C'
                else:
                    result.grade = 'D'
                
                result.status = 'pass'
            else:
                result.grade = 'F'
                result.status = 'fail'
            
            result.save()
            messages.success(request, f'Result for {result.student.name} updated successfully.')
            return redirect('result_detail', pk=pk)
    else:
        form = ResultForm(instance=result)
    
    context = {
        'form': form,
        'title': 'Update Result',
        'result': result,
    }
    
    return render(request, 'examination/result_form.html', context)

@login_required
@user_passes_test(is_admin_or_faculty)
def result_delete(request, pk):
    """View to delete a result"""
    result = get_object_or_404(Result, pk=pk)
    
    if request.method == 'POST':
        student_name = result.student.name
        result.delete()
        messages.success(request, f'Result for {student_name} deleted successfully.')
        return redirect('result_list')
    
    context = {
        # The confirmation template needs the named object to build result_id URLs.
        'result': result,
        'title': 'Delete Result',
    }
    
    return render(request, 'examination/result_confirm_delete.html', context)

@login_required
def student_results(request, student_id=None):
    """View to display results for a specific student or the logged-in student"""
    def build_student_results_context(student, results, title):
        result_list = list(results)
        total_exams = len(result_list)
        passed_exams = sum(1 for result in result_list if result.status == 'pass')
        pass_percentage = (passed_exams / total_exams * 100) if total_exams else 0
        avg_percentage = (
            sum(float(result.percentage or 0) for result in result_list) / total_exams
            if total_exams else 0
        )

        grade_distribution = {}
        for result in result_list:
            grade = result.grade or 'N/A'
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

        courses = {}
        for result in result_list:
            course_name = result.examination.course.name
            courses.setdefault(course_name, []).append(result)

        grade_rank = {'A+': 8, 'A': 7, 'B+': 6, 'B': 5, 'C+': 4, 'C': 3, 'D': 2, 'F': 1}

        def best_grade_for(items):
            grades = [item.grade for item in items if item.grade]
            return max(grades, key=lambda grade: grade_rank.get(grade, 0)) if grades else 'N/A'

        result_summaries = []
        for exam_type, label in Examination.EXAM_TYPES:
            typed_results = [result for result in result_list if result.examination.exam_type == exam_type]
            count = len(typed_results)
            average = (
                sum(float(result.percentage or 0) for result in typed_results) / count
                if count else 0
            )
            result_summaries.append({
                'label': label,
                'count': count,
                'average': average,
                'best_grade': best_grade_for(typed_results),
            })

        return {
            'student': student,
            'results': result_list,
            'title': title,
            'total_exams': total_exams,
            'passed_exams': passed_exams,
            'pass_percentage': pass_percentage,
            'avg_percentage': avg_percentage,
            'grade_distribution': grade_distribution,
            'courses': courses,
            'result_summaries': result_summaries,
            'overall_best_grade': best_grade_for(result_list),
        }

    # For a specific student (used by admin/faculty)
    if student_id:
        student = get_object_or_404(Student, pk=student_id)
        results = Result.objects.filter(student=student).order_by('-examination__date')
        context = build_student_results_context(student, results, f'Results for {student.name}')
        return render(request, 'examination/student_results.html', context)
    
    # For the logged-in student (my results)
    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'student':
        try:
            student = Student.objects.get(user=request.user)
            results = Result.objects.filter(student=student).order_by('-examination__date')
            context = build_student_results_context(student, results, 'My Results')
            return render(request, 'examination/student_results.html', context)
        except Student.DoesNotExist:
            messages.error(request, 'Student profile not found.')
            return redirect('home')
    
    # If not a student and no student_id provided
    messages.error(request, 'Please specify a student to view results.')
    return redirect('home')

@login_required
@user_passes_test(is_admin_or_faculty)
def bulk_result_create(request):
    """View to create results for multiple students at once"""
    if request.method == 'POST':
        form = BulkResultForm(request.POST)
        if form.is_valid():
            examination = form.cleaned_data['examination']
            course = examination.course
            students = Student.objects.filter(course=course)
            
            created_count = 0
            for student in students:
                marks_field = f'marks_{student.student_id}'
                status_field = f'status_{student.student_id}'
                remarks_field = f'remarks_{student.student_id}'
                
                if marks_field in form.cleaned_data:
                    marks_obtained = form.cleaned_data[marks_field]
                    status = form.cleaned_data.get(status_field, 'pass')
                    remarks = form.cleaned_data.get(remarks_field, '')
                    
                    # Calculate percentage
                    if examination.total_marks > 0:
                        percentage = (marks_obtained / examination.total_marks) * 100
                    else:
                        percentage = 0
                    
                    # Determine grade
                    if marks_obtained >= examination.passing_marks:
                        if percentage >= 90:
                            grade = 'A+'
                        elif percentage >= 80:
                            grade = 'A'
                        elif percentage >= 70:
                            grade = 'B+'
                        elif percentage >= 60:
                            grade = 'B'
                        elif percentage >= 50:
                            grade = 'C+'
                        elif percentage >= 40:
                            grade = 'C'
                        else:
                            grade = 'D'
                        
                        status = 'pass'
                    else:
                        grade = 'F'
                        status = 'fail'
                    
                    # Create or update the result
                    Result.objects.update_or_create(
                        student=student,
                        examination=examination,
                        defaults={
                            'marks_obtained': marks_obtained,
                            'percentage': percentage,
                            'grade': grade,
                            'status': status,
                            'remarks': remarks,
                        }
                    )
                    created_count += 1
            
            messages.success(request, f'Successfully created/updated {created_count} results for {examination.exam_name}.')
            return redirect('result_list')
    else:
        form = BulkResultForm()
    
    context = {
        'form': form,
        'title': 'Bulk Result Entry',
    }
    
    return render(request, 'examination/bulk_result_form.html', context)
