from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from .models import AuditTrail


def _request_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _request_user_agent(request):
    # AuditTrail.user_agent is capped at 255 chars.
    return (request.META.get('HTTP_USER_AGENT') or '')[:255]


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditTrail.objects.create(
        user=user,
        action='login',
        module='authentication',
        record_id=user.id,
        description=f'{user.get_username()} signed in',
        ip_address=_request_ip(request),
        user_agent=_request_user_agent(request),
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user is None:
        return

    AuditTrail.objects.create(
        user=user,
        action='logout',
        module='authentication',
        record_id=user.id,
        description=f'{user.get_username()} signed out',
        ip_address=_request_ip(request),
        user_agent=_request_user_agent(request),
    )
