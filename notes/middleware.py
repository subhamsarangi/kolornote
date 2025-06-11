import pytz
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, "timezone"):
            user_timezone = request.user.timezone
            try:
                timezone.activate(pytz.timezone(user_timezone))
            except pytz.exceptions.UnknownTimeZoneError:
                timezone.activate(pytz.UTC)
        else:
            timezone.deactivate()

        response = self.get_response(request)
        return response
