"""complaints URL configuration."""

from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('',                      views.ComplaintListView.as_view(),   name='list'),
    path('<int:pk>/',              views.ComplaintDetailView.as_view(), name='detail'),
    path('new/',                   views.ComplaintCreateView.as_view(), name='create'),
    path('<int:pk>/edit/',         views.ComplaintUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/',       views.ComplaintDeleteView.as_view(), name='delete'),
    path('<int:pk>/status/',       views.update_status,                 name='update_status'),
    path('notifications/',         views.notifications,                 name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_read'),
]
