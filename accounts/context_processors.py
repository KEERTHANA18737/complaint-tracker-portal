"""
Injects the unread notification count into every template context
so the navbar bell icon always shows the correct badge.
"""


def notification_count(request):
    count = 0
    if request.user.is_authenticated:
        from complaints.models import Notification
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {'unread_notification_count': count}
