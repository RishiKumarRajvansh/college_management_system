from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views import View
from django.urls import reverse_lazy
from .forms import LoginForm

class CustomLoginView(LoginView):
    """Custom login view that redirects authenticated users to the dashboard"""
    template_name = 'user_authentication/login.html'
    form_class = LoginForm
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # Redirect to home if already logged in
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Override to check if this is the first login"""
        response = super().form_valid(form)
        
        user = self.request.user
        # Check if this is likely the first login (date_joined == last_login)
        if user.last_login and user.date_joined.date() == user.last_login.date():
            # Check if the username is an email (our auto-generated accounts)
            if user.username == user.email:
                # Redirect to force password change
                return redirect('force_password_change')
        
        return response
