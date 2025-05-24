from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile, PasswordResetRequest
import random
import string

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))

class UserRegistrationForm(UserCreationForm):
    USER_TYPES = (
        ('admin', 'Administrator'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    )
    
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    user_type = forms.ChoiceField(choices=USER_TYPES, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Also check if any user has this email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists. Please use a different email.")
            
        # For student/faculty specific validation, we need user_type
        user_type = self.data.get('user_type')  # Access from raw data instead of cleaned_data
        
        # Import here to avoid circular imports
        if user_type == 'student':
            from student_management.models import Student
            if Student.objects.filter(email=email).exists():
                raise forms.ValidationError("A student with this email already exists. Please use a different email.")
        elif user_type == 'faculty':
            from faculty_management.models import Faculty
            if Faculty.objects.filter(email=email).exists():
                raise forms.ValidationError("A faculty member with this email already exists. Please use a different email.")
            
        return email

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address', 'date_of_birth', 'profile_picture')
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Old Password'
    }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Password'
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm New Password'
    }))
    
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

class PasswordResetRequestForm(forms.Form):
    username = forms.CharField(label='Username or Email', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your username or email',
    }))

    def clean_username(self):
        username_or_email = self.cleaned_data.get('username')
        
        # Check if the user exists
        user = User.objects.filter(username=username_or_email).first()
        if not user:
            # Try with email
            user = User.objects.filter(email=username_or_email).first()
        
        if not user:
            raise forms.ValidationError("No user found with this username or email address.")
            
        return username_or_email

class AdminPasswordResetForm(forms.ModelForm):
    new_password = forms.CharField(label='New Password', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter new password',
    }))
    
    class Meta:
        model = PasswordResetRequest
        fields = ['status', 'notes', 'new_password']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generate a random password as suggestion
        random_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        self.fields['new_password'].initial = random_password
        self.fields['new_password'].help_text = 'You can use this randomly generated password or create your own.'
        
    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        status = self.cleaned_data.get('status')
        
        if status == 'processed' and (not password or len(password) < 8):
            raise forms.ValidationError("Password must be at least 8 characters long.")
            
        return password
