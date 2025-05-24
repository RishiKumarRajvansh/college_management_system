from django import forms
from .models import Student
from course_management.models import Course

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('name', 'email', 'course', 'year')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        instance = getattr(self, 'instance', None)
        
        # Check if this email already exists
        if Student.objects.filter(email=email).exclude(pk=instance.pk if instance and instance.pk else None).exists():
            raise forms.ValidationError("A student with this email already exists.")
        
        return email

class StudentSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Name, Email, or ID'})
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
