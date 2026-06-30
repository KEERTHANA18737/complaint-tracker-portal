"""
complaints/views.py
Class-based views for complaint lifecycle management.
Citizens submit/edit their own complaints.
Officers/Admins manage status, assignment, and priority.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView)
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Complaint, ComplaintHistory, Notification, Category
from .forms import ComplaintForm, StatusUpdateForm, SearchForm
from accounts.models import User


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------
class OfficerRequiredMixin(UserPassesTestMixin):
    """Allow access only to officers and admins."""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.can_manage_complaints


# ---------------------------------------------------------------------------
# Complaint List (with search/filter/pagination)
# ---------------------------------------------------------------------------
class ComplaintListView(LoginRequiredMixin, ListView):
    """
    Shows all complaints (officers/admins) or only the citizen's own complaints.
    Supports search, filter, and sort via GET params.
    """
    model               = Complaint
    template_name       = 'complaints/complaint_list.html'
    context_object_name = 'complaints'
    paginate_by         = 10

    def get_queryset(self):
        user = self.request.user
        qs   = Complaint.objects.select_related('citizen', 'category', 'assigned_to')

        # Citizens only see their own complaints
        if user.is_citizen:
            qs = qs.filter(citizen=user)

        form = SearchForm(self.request.GET)
        if form.is_valid():
            q        = form.cleaned_data.get('q')
            status   = form.cleaned_data.get('status')
            priority = form.cleaned_data.get('priority')
            category = form.cleaned_data.get('category')
            officer  = form.cleaned_data.get('officer')
            sort     = form.cleaned_data.get('sort') or '-created_at'

            if q:
                qs = qs.filter(
                    Q(title__icontains=q) |
                    Q(location__icontains=q) |
                    Q(description__icontains=q))
            if status:
                qs = qs.filter(status=status)
            if priority:
                qs = qs.filter(priority=priority)
            if category:
                qs = qs.filter(category=category)
            if officer:
                qs = qs.filter(assigned_to=officer)

            qs = qs.order_by(sort)
        else:
            qs = qs.order_by('-created_at')

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['search_form'] = SearchForm(self.request.GET)
        ctx['categories']  = Category.objects.all()
        ctx['total']       = self.get_queryset().count()
        return ctx


# ---------------------------------------------------------------------------
# Complaint Detail
# ---------------------------------------------------------------------------
class ComplaintDetailView(LoginRequiredMixin, DetailView):
    """Shows full complaint details, timeline history, and the status-update form."""

    model               = Complaint
    template_name       = 'complaints/complaint_detail.html'
    context_object_name = 'complaint'

    def get_object(self):
        obj  = get_object_or_404(Complaint, pk=self.kwargs['pk'])
        user = self.request.user
        # Citizens can only view their own complaints
        if user.is_citizen and obj.citizen != user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['history']     = self.object.history.select_related('changed_by').all()
        ctx['status_form'] = StatusUpdateForm(instance=self.object)
        return ctx


# ---------------------------------------------------------------------------
# Submit Complaint
# ---------------------------------------------------------------------------
class ComplaintCreateView(LoginRequiredMixin, CreateView):
    """Citizens submit a new complaint."""

    model         = Complaint
    form_class    = ComplaintForm
    template_name = 'complaints/complaint_form.html'

    def form_valid(self, form):
        complaint          = form.save(commit=False)
        complaint.citizen  = self.request.user
        complaint.save()
        messages.success(self.request, f'Complaint #{complaint.pk} submitted successfully.')
        return redirect('complaints:detail', pk=complaint.pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_title'] = 'Submit New Complaint'
        return ctx


# ---------------------------------------------------------------------------
# Edit Complaint (Citizen edits own; officer/admin can edit all)
# ---------------------------------------------------------------------------
class ComplaintUpdateView(LoginRequiredMixin, UpdateView):
    """Edit the basic fields of a complaint."""

    model         = Complaint
    form_class    = ComplaintForm
    template_name = 'complaints/complaint_form.html'

    def get_object(self):
        obj  = get_object_or_404(Complaint, pk=self.kwargs['pk'])
        user = self.request.user
        if user.is_citizen and obj.citizen != user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        messages.success(self.request, 'Complaint updated.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('complaints:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form_title'] = 'Edit Complaint'
        return ctx


# ---------------------------------------------------------------------------
# Delete Complaint
# ---------------------------------------------------------------------------
class ComplaintDeleteView(LoginRequiredMixin, DeleteView):
    """Citizens delete their own complaints; admins delete any."""

    model         = Complaint
    template_name = 'complaints/complaint_confirm_delete.html'
    success_url   = reverse_lazy('complaints:list')

    def get_object(self):
        obj  = get_object_or_404(Complaint, pk=self.kwargs['pk'])
        user = self.request.user
        if user.is_citizen and obj.citizen != user:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        messages.success(self.request, 'Complaint deleted.')
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Status Update (Officer / Admin only)
# ---------------------------------------------------------------------------
@login_required
def update_status(request, pk):
    """AJAX-friendly POST endpoint for officers/admins to update complaint status."""
    complaint = get_object_or_404(Complaint, pk=pk)

    if not request.user.can_manage_complaints:
        messages.error(request, 'You do not have permission to update complaint status.')
        return redirect('complaints:detail', pk=pk)

    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            updated         = form.save(commit=False)
            updated._changed_by = request.user
            updated._remarks    = form.cleaned_data.get('remarks', '')
            updated.save()
            messages.success(request, f'Complaint #{pk} updated successfully.')
        else:
            messages.error(request, 'Invalid form data.')

    return redirect('complaints:detail', pk=pk)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------
@login_required
def notifications(request):
    """List all notifications; mark them read."""
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'complaints/notifications.html', {'notifications': notifs})


@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    return redirect('complaints:notifications')


# ---------------------------------------------------------------------------
# Error pages
# ---------------------------------------------------------------------------
def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
