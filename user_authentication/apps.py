from django.apps import AppConfig


class UserAuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_authentication'

    def ready(self):
        # Register auth signal handlers so login/logout activity is captured centrally.
        from . import signals  # noqa: F401
