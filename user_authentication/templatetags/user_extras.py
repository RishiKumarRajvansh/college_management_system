from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def get_yesterday(value):
    """Returns yesterday's date based on the provided date string in YYYY-MM-DD format"""
    if not value:
        return None
    try:
        date_obj = datetime.strptime(value, '%Y-%m-%d')
        yesterday = date_obj - timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        return None
