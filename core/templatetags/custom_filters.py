from django import template

register = template.Library()

@register.filter(name='category_badge')
def category_badge(category):
    badge_classes = {
        'featured': 'primary',
        'today': 'success',
        'tomorrow': 'info',
        'this_week': 'warning',
        'upcoming': 'secondary'
    }
    return badge_classes.get(category, 'secondary')

@register.filter(name='event_type_badge')
def event_type_badge(event_type):
    badge_classes = {
        'environmental': 'success',
        'educational': 'info',
        'social': 'primary',
        'health': 'danger',
        'cultural': 'warning',
        'emergency': 'danger',
        'community': 'success',
        'youth': 'info',
        'senior': 'warning',
        'animal': 'success'
    }
    return badge_classes.get(event_type.lower(), 'secondary')

@register.filter
def split(value, arg):
    return [item.strip() for item in value.split(arg)]

@register.filter(name='subtract')
def subtract(value, arg):
    """Subtract the arg from the value"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value

@register.filter(name='percentage')
def percentage(value, arg):
    """Calculate percentage"""
    try:
        return int((float(value) / float(arg)) * 100)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0