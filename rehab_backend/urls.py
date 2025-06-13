from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from patients.views import register
from debug_toolbar import urls

# URL patterns for the main project
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register, name='register'),
    
    # API endpoints (v1)
    path('api/v1/', include('patients.api.urls')),
    
    # Web interface
    path('patients/', include('patients.urls', namespace='patients')),
    path('appointments/', include('appointments.urls', namespace='appointments')),
]

# Debug configurations
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]

# Static and media files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)