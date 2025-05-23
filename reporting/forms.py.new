from django import forms
from .models import Report
from student_management.models import Student
from faculty_management.models import Faculty
from course_management.models import Course
from library_management.models import Book, BookIssue
from hostel_management.models import Hostel, Room, HostelAllocation

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('title', 'description', 'report_type', 'parameters', 'is_scheduled', 'schedule_frequency')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'parameters': forms.JSONField(widget=forms.Textarea(attrs={'class': 'form-control'})),
            'is_scheduled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'schedule_frequency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'daily, weekly, monthly'}),
        }

class StudentReportForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Courses"
    )
    year = forms.ChoiceField(
        choices=[(0, 'All Years')] + [(i, i) for i in range(1, 6)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    format = forms.ChoiceField(
        choices=[('pdf', 'PDF'), ('excel', 'Excel')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class FacultyReportForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    format = forms.ChoiceField(
        choices=[('pdf', 'PDF'), ('excel', 'Excel')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class AttendanceReportForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Courses"
    )
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Students"
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    format = forms.ChoiceField(
        choices=[('pdf', 'PDF'), ('excel', 'Excel')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ExaminationReportForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Courses"
    )
    exam_type = forms.ChoiceField(
        choices=[('', 'All Types')] + [('midterm', 'Mid Term'), ('final', 'Final Exam'), ('quiz', 'Quiz'), ('assignment', 'Assignment'), ('project', 'Project')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    format = forms.ChoiceField(
        choices=[('pdf', 'PDF'), ('excel', 'Excel')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class FeeReportForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    format = forms.ChoiceField(
        choices=[('pdf', 'PDF'), ('excel', 'Excel')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ReportSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Report Title'})
    )
    
    report_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Report.REPORT_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_scheduled = forms.ChoiceField(
        choices=[('', 'All Reports'), ('True', 'Scheduled Only'), ('False', 'One-time Only')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class LibraryReportForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    book_status = forms.ChoiceField(
        choices=[('', 'All Books'), ('available', 'Available Books'), ('borrowed', 'Borrowed Books')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_range = forms.ChoiceField(
        choices=[
            ('all', 'All Time'),
            ('7days', 'Last 7 Days'),
            ('30days', 'Last 30 Days'),
            ('90days', 'Last 90 Days'),
            ('custom', 'Custom Range')
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'library-date-range'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    format = forms.ChoiceField(
        choices=[('pdf', 'PDF'), ('excel', 'Excel')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class HostelReportForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    hostel = forms.ModelChoiceField(
        queryset=Hostel.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Hostels"
    )
    room_status = forms.ChoiceField(
        choices=[
            ('', 'All Rooms'),
            ('available', 'Available Rooms'),
            ('occupied', 'Occupied Rooms'),
            ('maintenance', 'Rooms Under Maintenance')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    allocation_status = forms.ChoiceField(
        choices=[
            ('', 'All Allocations'),
            ('active', 'Active Allocations'),
            ('inactive', 'Past Allocations')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_range = forms.ChoiceField(
        choices=[
            ('all', 'All Time'),
            ('7days', 'Last 7 Days'),
            ('30days', 'Last 30 Days'),
            ('90days', 'Last 90 Days'),
            ('custom', 'Custom Range')
        ],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'hostel-date-range'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    format = forms.ChoiceField(
        choices=[('pdf', 'PDF'), ('excel', 'Excel')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
