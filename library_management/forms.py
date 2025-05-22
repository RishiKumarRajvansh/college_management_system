from django import forms
from .models import Book, BookIssue
from student_management.models import Student
from datetime import datetime, timedelta

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('title', 'author', 'isbn', 'publication', 'availability')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'publication': forms.TextInput(attrs={'class': 'form-control'}),
            'availability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BookIssueForm(forms.ModelForm):
    return_date = forms.DateField(
        initial=datetime.now().date() + timedelta(days=14),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    class Meta:
        model = BookIssue
        fields = ('student', 'book', 'return_date')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'book': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(BookIssueForm, self).__init__(*args, **kwargs)
        # Only show available books in the dropdown
        self.fields['book'].queryset = Book.objects.filter(availability=True)

class BookReturnForm(forms.ModelForm):
    actual_return_date = forms.DateField(
        initial=datetime.now().date(),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    class Meta:
        model = BookIssue
        fields = ('actual_return_date', 'fine_amount')
        widgets = {
            'fine_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

class BookSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Title, Author, or ISBN'})
    )
    availability = forms.ChoiceField(
        choices=[('', 'All Books'), ('True', 'Available Only'), ('False', 'Checked Out Only')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class BookIssueSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Book Title or Student Name'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('False', 'Checked Out'), ('True', 'Returned')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Students"
    )
    issue_date_start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    issue_date_end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
