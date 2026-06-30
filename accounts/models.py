"""
accounts/models.py
Custom User model extending AbstractUser with role-based access control.
Roles: CITIZEN | OFFICER | ADMIN
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model with role, phone, and avatar."""

    ROLE_CITIZEN = 'citizen'
    ROLE_OFFICER = 'officer'
    ROLE_ADMIN   = 'admin'

    ROLE_CHOICES = [
        (ROLE_CITIZEN, 'Citizen'),
        (ROLE_OFFICER, 'Officer'),
        (ROLE_ADMIN,   'Admin'),
    ]

    role    = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CITIZEN)
    phone   = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    avatar  = models.ImageField(upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name      = 'User'
        verbose_name_plural = 'Users'
        indexes = [models.Index(fields=['role'])]

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------
    @property
    def is_citizen(self):
        return self.role == self.ROLE_CITIZEN

    @property
    def is_officer(self):
        return self.role == self.ROLE_OFFICER

    @property
    def is_admin_role(self):
        return self.role == self.ROLE_ADMIN

    @property
    def can_manage_complaints(self):
        """Officers and Admins can update complaint status / assign."""
        return self.role in (self.ROLE_OFFICER, self.ROLE_ADMIN)

    def get_role_badge(self):
        badges = {
            self.ROLE_CITIZEN: 'bg-secondary',
            self.ROLE_OFFICER: 'bg-primary',
            self.ROLE_ADMIN:   'bg-danger',
        }
        return badges.get(self.role, 'bg-secondary')

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'
