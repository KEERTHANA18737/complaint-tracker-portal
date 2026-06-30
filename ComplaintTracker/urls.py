"""
ComplaintTracker URL Configuration
Root URL dispatcher – delegates to each app's url module.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('accounts/', include('accounts.urls',   namespace='accounts')),
    path('dashboard/',include('dashboard.urls',  namespace='dashboard')),
    path('complaints/',include('complaints.urls', namespace='complaints')),
    # Redirect root → dashboard
    path('', __import__('django.views.generic', fromlist=['RedirectView']).RedirectView.as_view(url='/dashboard/'), name='root'),
]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'complaints.views.error_404'
handler500 = 'complaints.views.error_500'
