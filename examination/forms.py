# filepath: d:\mca project 5\examination\forms.py
from django import forms
from .models import Examination, Result
from student_management.models import Student
from course_management.models import Course

class ExaminationForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = ('exam_name', 'exam_type', 'course', 'date', 'duration', 'total_marks', 'passing_marks')
        widgets = {
            'exam_name': forms.TextInput(attrs={'class': 'form-control'}),
            'exam_type': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'passing_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ('student', 'examination', 'marks_obtained', 'remarks')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'examination': forms.Select(attrs={'class': 'form-control'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BulkResultForm(forms.Form):
    examination = forms.ModelChoiceField(
        queryset=Examination.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super(BulkResultForm, self).__init__(*args, **kwargs)
        if 'examination' in self.data:
            try:
                exam_id = int(self.data.get('examination'))
                exam = Examination.objects.get(pk=exam_id)
                students = Student.objects.filter(course=exam.course)
                for student in students:
                    field_name = f'marks_{student.student_id}'
                    remarks_field = f'remarks_{student.student_id}'
                    self.fields[field_name] = forms.DecimalField(
                        label=f"Marks for {student.name}",
                        max_digits=5,
                        decimal_places=2,
                        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': exam.total_marks})
                    )
                    self.fields[remarks_field] = forms.CharField(
                        label=f"Remarks for {student.name}",
                        required=False,
                        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
                    )
            except (ValueError, TypeError, Examination.DoesNotExist):
                pass

class ExaminationSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Name or ID'})
    )
    exam_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Examination.EXAM_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
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

class ResultSearchForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Students"
    )
    examination = forms.ModelChoiceField(
        queryset=Examination.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Examinations"
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Result.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    grade = forms.ChoiceField(
        choices=[('', 'All Grades')] + list(Result.GRADE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
