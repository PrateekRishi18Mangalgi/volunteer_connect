from django import template
from django.db.models import Avg
from core.models import EventFeedback

register = template.Library()

@register.filter
def has_feedback(event, user):
    """Check if a user has provided feedback for an event"""
    return EventFeedback.objects.filter(event=event, volunteer=user).exists()

@register.filter
def get_user_feedback(event, user):
    """Get the user's feedback for an event"""
    return EventFeedback.objects.filter(event=event, volunteer=user).first()

@register.filter
def avg_rating(event):
    """Calculate average rating for an event"""
    avg = EventFeedback.objects.filter(event=event).aggregate(Avg('rating'))['rating__avg']
    return round(avg, 1) if avg else 0