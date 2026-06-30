"""
complaints/admin.py
Customised Django admin with search, filters, list display,
and inline ComplaintHistory on the Complaint change page.
"""

from django.contrib import admin
from .models import Category, Complaint, ComplaintHistory, Notification


class ComplaintHistoryInline(admin.TabularInline):
    model  = ComplaintHistory
    extra  = 0
    fields = ('old_status', 'new_status', 'changed_by', 'timestamp', 'remarks')
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'timestamp')
    can_delete = False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display   = ('id', 'title', 'citizen', 'category', 'status',
                      'priority', 'assigned_to', 'created_at')
    list_filter    = ('status', 'priority', 'category')
    search_fields  = ('title', 'location', 'citizen__username', 'citizen__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines        = [ComplaintHistoryInline]
    date_hierarchy = 'created_at'
    ordering       = ('-created_at',)

    fieldsets = (
        ('Complaint Info', {
            'fields': ('citizen', 'title', 'description', 'category', 'location', 'image')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'priority', 'assigned_to', 'latitude', 'longitude')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ComplaintHistory)
class ComplaintHistoryAdmin(admin.ModelAdmin):
    list_display  = ('complaint', 'old_status', 'new_status', 'changed_by', 'timestamp')
    list_filter   = ('new_status',)
    search_fields = ('complaint__title',)
    readonly_fields = ('complaint', 'old_status', 'new_status', 'changed_by', 'timestamp')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('user', 'complaint', 'message', 'is_read', 'created_at')
    list_filter   = ('is_read',)
    search_fields = ('user__username', 'message')
