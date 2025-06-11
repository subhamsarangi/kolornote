from django import template
from django.utils import timezone
from django.utils.dateformat import format as dj_format
import pytz

register = template.Library()


@register.filter
def user_timezone(value, user):
    """Convert datetime to user's timezone"""
    if not user.is_authenticated or not hasattr(user, "timezone"):
        return value

    try:
        user_tz = pytz.timezone(user.timezone)
        return value.astimezone(user_tz)
    except (pytz.exceptions.UnknownTimeZoneError, AttributeError):
        return value


@register.simple_tag
def user_current_time(user):
    """Get current time in user's timezone formatted like 'June 10, 2025 8:49 AM'"""
    if not user.is_authenticated or not hasattr(user, "timezone"):
        current_time = timezone.now()
    else:
        try:
            user_tz = pytz.timezone(user.timezone)
            current_time = timezone.now().astimezone(user_tz)
        except pytz.exceptions.UnknownTimeZoneError:
            current_time = timezone.now()

    # Format datetime: 'F d, Y g:i A' => 'June 10, 2025 8:49 AM'
    return dj_format(current_time, "F d, Y g:i A")
