"""
complaints/signals.py
Django signals that fire on Complaint save to:
  1. Record a history entry whenever status changes.
  2. Notify the citizen when their complaint status is updated.
"""

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Complaint, ComplaintHistory, Notification


@receiver(pre_save, sender=Complaint)
def capture_old_status(sender, instance, **kwargs):
    """Store the current status on the instance before it is overwritten."""
    if instance.pk:
        try:
            instance._old_status = Complaint.objects.get(pk=instance.pk).status
        except Complaint.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Complaint)
def create_history_and_notify(sender, instance, created, **kwargs):
    """After a Complaint is saved, record history and send notification if status changed."""
    old_status = getattr(instance, '_old_status', None)

    if created:
        # Record initial status
        ComplaintHistory.objects.create(
            complaint=instance,
            old_status='',
            new_status=instance.status,
            changed_by=instance.citizen,
            remarks='Complaint submitted.',
        )
        return

    if old_status and old_status != instance.status:
        # Record the transition (changed_by is set on the instance by the view)
        changed_by = getattr(instance, '_changed_by', None)
        remarks    = getattr(instance, '_remarks', '')

        ComplaintHistory.objects.create(
            complaint=instance,
            old_status=old_status,
            new_status=instance.status,
            changed_by=changed_by,
            remarks=remarks,
        )

        # Notify the citizen
        Notification.objects.create(
            user=instance.citizen,
            complaint=instance,
            message=(
                f'Your complaint "{instance.title}" status changed '
                f'from "{old_status.replace("_", " ").title()}" '
                f'to "{instance.get_status_display()}".'
            ),
        )
