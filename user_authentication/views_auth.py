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
