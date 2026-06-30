"""dashboard URL configuration."""

from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',      views.index, name='index'),
    # Root redirect: / → /dashboard/
    path('',      RedirectView.as_view(pattern_name='dashboard:index'), name='root'),
]
