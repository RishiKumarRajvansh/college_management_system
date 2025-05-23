from django import template

register = template.Library()

@register.filter
def getattribute(obj, attr):
    """Gets an attribute from an object dynamically from a string name"""
    if hasattr(obj, attr):
        return getattr(obj, attr)
    elif hasattr(obj, '__getitem__') and attr in obj:
        return obj[attr]
    else:
        return None

@register.filter
def getattributeerrors(obj, attr):
    """Gets errors for a form field dynamically"""
    if hasattr(obj, 'errors') and attr in obj.errors:
        return obj.errors[attr]
    else:
        return None
