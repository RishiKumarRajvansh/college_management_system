from django.shortcuts import redirect
from django.urls import reverse
from re import compile

class ForcePasswordChangeMiddleware:
    """
    Middleware to force password change for users on first login
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Paths that do not require password change
        self.exempt_urls = [
            compile(r'^/auth/logout/.*$'),  # logout
            compile(r'^/auth/force-password-change/.*$'),  # force password change
            compile(r'^/auth/password-reset/.*$'),  # password reset
            compile(r'^/static/.*$'),  # static files
            # Add any other exempt paths here
        ]

    def __call__(self, request):
        # Skip middleware if user is not authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Check if the user profile exists and requires a password change
        if hasattr(request.user, 'profile') and request.user.profile.is_first_login:
            # Check if the current URL is on the exempt list
            path = request.path_info.lstrip('/')
            full_path = request.get_full_path()
            
            # Exempt URLs and admin users
            if any(m.match(full_path) for m in self.exempt_urls) or request.user.is_superuser:
                return self.get_response(request)
              # Redirect to force password change
            return redirect('auth:force_password_change')
            
        return self.get_response(request)
