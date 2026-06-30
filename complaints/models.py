"""
complaints/models.py
Core domain models: Category, Complaint, ComplaintHistory, Notification.
Uses signals to auto-create history records on status change.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------
class Category(models.Model):
    """Complaint category (e.g. Roads, Water, Electricity)."""

    name        = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=50, default='bi-tag', help_text='Bootstrap Icons class')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Complaint
# ---------------------------------------------------------------------------
class Complaint(models.Model):
    """A complaint filed by a citizen."""

    # Status choices
    STATUS_PENDING     = 'pending'
    STATUS_ASSIGNED    = 'assigned'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED    = 'resolved'
    STATUS_CLOSED      = 'closed'

    STATUS_CHOICES = [
        (STATUS_PENDING,     'Pending'),
        (STATUS_ASSIGNED,    'Assigned'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_RESOLVED,    'Resolved'),
        (STATUS_CLOSED,      'Closed'),
    ]

    # Priority choices
    PRIORITY_LOW      = 'low'
    PRIORITY_MEDIUM   = 'medium'
    PRIORITY_HIGH     = 'high'
    PRIORITY_CRITICAL = 'critical'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW,      'Low'),
        (PRIORITY_MEDIUM,   'Medium'),
        (PRIORITY_HIGH,     'High'),
        (PRIORITY_CRITICAL, 'Critical'),
    ]

    citizen     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='complaints', limit_choices_to={'role': 'citizen'})
    title       = models.CharField(max_length=200)
    description = models.TextField()
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                    null=True, related_name='complaints')
    location    = models.CharField(max_length=255)
    image       = models.ImageField(upload_to='complaint_images/%Y/%m/', blank=True, null=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_complaints',
        limit_choices_to={'role__in': ['officer', 'admin']})
    latitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude   = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['citizen']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f'#{self.pk} – {self.title}'

    # ------------------------------------------------------------------
    # Badge helpers for templates
    # ------------------------------------------------------------------
    def get_status_badge(self):
        badges = {
            self.STATUS_PENDING:     'badge-pending',
            self.STATUS_ASSIGNED:    'badge-assigned',
            self.STATUS_IN_PROGRESS: 'badge-progress',
            self.STATUS_RESOLVED:    'badge-resolved',
            self.STATUS_CLOSED:      'badge-closed',
        }
        return badges.get(self.status, 'bg-secondary')

    def get_priority_badge(self):
        badges = {
            self.PRIORITY_LOW:      'badge-low',
            self.PRIORITY_MEDIUM:   'badge-medium',
            self.PRIORITY_HIGH:     'badge-high',
            self.PRIORITY_CRITICAL: 'badge-critical',
        }
        return badges.get(self.priority, 'bg-secondary')

    def get_status_icon(self):
        icons = {
            self.STATUS_PENDING:     'bi-clock',
            self.STATUS_ASSIGNED:    'bi-person-check',
            self.STATUS_IN_PROGRESS: 'bi-arrow-repeat',
            self.STATUS_RESOLVED:    'bi-check-circle',
            self.STATUS_CLOSED:      'bi-x-circle',
        }
        return icons.get(self.status, 'bi-question-circle')


# ---------------------------------------------------------------------------
# ComplaintHistory
# ---------------------------------------------------------------------------
class ComplaintHistory(models.Model):
    """Immutable audit log of every status change on a complaint."""

    complaint  = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    timestamp  = models.DateTimeField(default=timezone.now)
    remarks    = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Complaint histories'

    def __str__(self):
        return f'{self.complaint} | {self.old_status} → {self.new_status}'


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------
class Notification(models.Model):
    """In-app notification sent to a user about a complaint event."""

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='notifications')
    complaint  = models.ForeignKey(Complaint, on_delete=models.CASCADE,
                                   related_name='notifications', null=True, blank=True)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user} – {self.message[:50]}'
