from django import forms
from .models import Attendance
from student_management.models import Student
from course_management.models import Course

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ('student', 'course', 'date', 'status')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class BulkAttendanceForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        super(BulkAttendanceForm, self).__init__(*args, **kwargs)
        if 'course' in self.data:
            try:
                course_id = int(self.data.get('course'))
                students = Student.objects.filter(course_id=course_id)
                for student in students:
                    field_name = f'student_{student.student_id}'
                    self.fields[field_name] = forms.ChoiceField(
                        label=student.name,
                        choices=Attendance.ATTENDANCE_STATUS,
                        widget=forms.Select(attrs={'class': 'form-control'})
                    )
            except (ValueError, TypeError):
                pass

class AttendanceSearchForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Students"
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Courses"
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Attendance.ATTENDANCE_STATUS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
