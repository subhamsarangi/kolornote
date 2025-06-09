from django.utils.timezone import now


def add_timestamp(request):
    return {"timestamp": int(now().timestamp())}
