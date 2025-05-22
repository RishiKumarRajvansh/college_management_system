from django import forms
from .models import FeeCategory, FeeStructure, Payment
from student_management.models import Student
from course_management.models import Course
import uuid

class FeeCategoryForm(forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ('category', 'course', 'amount', 'academic_year', 'due_date')
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2023-2024'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class PaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:  # Only for new payments
            self.initial['receipt_number'] = f"RCT-{uuid.uuid4().hex[:8].upper()}"
    
    class Meta:
        model = Payment
        fields = ('student', 'fee_structure', 'amount', 'payment_method', 'transaction_id', 'status', 'receipt_number', 'remarks')
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'fee_structure': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'receipt_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FeeCategorySearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Category Name'})
    )

class FeeStructureSearchForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=FeeCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Categories"
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Courses"
    )
    academic_year = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2023-2024'})
    )
    due_date_start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    due_date_end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

class PaymentSearchForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by Receipt# or Transaction ID'})
    )
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Students"
    )
    fee_category = forms.ModelChoiceField(
        queryset=FeeCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="All Categories"
    )
    payment_method = forms.ChoiceField(
        choices=[('', 'All Methods')] + list(Payment.PAYMENT_METHODS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Payment.PAYMENT_STATUS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    payment_date_start = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    payment_date_end = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
