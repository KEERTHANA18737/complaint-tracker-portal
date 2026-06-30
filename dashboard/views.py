"""
dashboard/views.py
Role-aware dashboard that returns statistics and chart data
for the Chart.js widgets embedded in dashboard.html.
"""

import json
from datetime import date, timedelta
from collections import defaultdict

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.utils import timezone

from complaints.models import Complaint, Category, Notification
from accounts.models import User


@login_required
def index(request):
    """
    Main dashboard view.
    Returns different context depending on user role.
    """
    user = request.user
    qs   = Complaint.objects.all()

    # Citizens only see their own complaints
    if user.is_citizen:
        qs = qs.filter(citizen=user)

    # ------------------------------------------------------------------
    # Statistics cards
    # ------------------------------------------------------------------
    stats = {
        'total':       qs.count(),
        'pending':     qs.filter(status=Complaint.STATUS_PENDING).count(),
        'in_progress': qs.filter(status=Complaint.STATUS_IN_PROGRESS).count(),
        'resolved':    qs.filter(status=Complaint.STATUS_RESOLVED).count(),
        'closed':      qs.filter(status=Complaint.STATUS_CLOSED).count(),
        'critical':    qs.filter(priority=Complaint.PRIORITY_CRITICAL).count(),
    }

    # ------------------------------------------------------------------
    # Latest 5 complaints
    # ------------------------------------------------------------------
    latest = qs.select_related('citizen', 'category', 'assigned_to').order_by('-created_at')[:5]

    # ------------------------------------------------------------------
    # Category distribution (for doughnut chart)
    # ------------------------------------------------------------------
    cat_data = (
        qs.values('category__name')
          .annotate(count=Count('id'))
          .order_by('-count')
    )
    category_labels = [d['category__name'] or 'Uncategorised' for d in cat_data]
    category_counts = [d['count'] for d in cat_data]

    # ------------------------------------------------------------------
    # Monthly trend – last 6 months (for bar chart)
    # ------------------------------------------------------------------
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_data = (
        qs.filter(created_at__gte=six_months_ago)
          .annotate(month=TruncMonth('created_at'))
          .values('month')
          .annotate(count=Count('id'))
          .order_by('month')
    )
    monthly_labels = [d['month'].strftime('%b %Y') for d in monthly_data]
    monthly_counts = [d['count'] for d in monthly_data]

    # ------------------------------------------------------------------
    # Status breakdown (for pie chart)
    # ------------------------------------------------------------------
    status_data   = qs.values('status').annotate(count=Count('id'))
    status_labels = [d['status'].replace('_', ' ').title() for d in status_data]
    status_counts = [d['count'] for d in status_data]

    # ------------------------------------------------------------------
    # Officer-specific: my assigned complaints
    # ------------------------------------------------------------------
    my_assigned = []
    if user.can_manage_complaints:
        my_assigned = Complaint.objects.filter(
            assigned_to=user, status=Complaint.STATUS_IN_PROGRESS
        ).select_related('citizen', 'category')[:5]

    context = {
        'stats':            stats,
        'latest':           latest,
        'my_assigned':      my_assigned,
        'category_labels':  json.dumps(category_labels),
        'category_counts':  json.dumps(category_counts),
        'monthly_labels':   json.dumps(monthly_labels),
        'monthly_counts':   json.dumps(monthly_counts),
        'status_labels':    json.dumps(status_labels),
        'status_counts':    json.dumps(status_counts),
    }

    return render(request, 'dashboard/dashboard.html', context)
