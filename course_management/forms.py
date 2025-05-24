from django import forms
from .models import Course
from faculty_management.models import Faculty

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('code', 'name', 'faculty', 'description', 'credits')
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Code (e.g., CS101)'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Name'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }

class CourseSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Course Name or ID'})
    )
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Faculty"
    )
    credits = forms.ChoiceField(
        choices=[(0, 'All Credits')] + [(i, i) for i in range(1, 11)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
