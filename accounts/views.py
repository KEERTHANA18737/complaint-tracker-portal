"""
accounts/views.py
Handles registration, login, logout, profile, and password reset.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .forms import RegistrationForm, LoginForm, ProfileForm
from .models import User


class RegisterView(CreateView):
    """Public registration page – creates a Citizen account."""

    template_name = 'accounts/register.html'
    form_class    = RegistrationForm
    success_url   = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Please sign in.')
        return response


def login_view(request):
    """Custom login that redirects based on role after successful auth."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.first_name or user.username}!')
        next_url = request.GET.get('next', 'dashboard:index')
        return redirect(next_url)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, UpdateView):
    """User can view and edit their own profile."""

    template_name = 'accounts/profile.html'
    form_class    = ProfileForm
    success_url   = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)
