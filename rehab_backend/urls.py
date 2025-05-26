from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# URL patterns for the main project
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints (v1)
    path('api/v1/', include('patients.api.urls')),
    
    # Web interface
    path('', include('patients.urls', namespace='patients')),
]

# Static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Debug configurations
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)