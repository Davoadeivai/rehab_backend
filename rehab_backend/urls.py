from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from patients.views import register, home
from debug_toolbar import urls
from users import views as user_views

# URL patterns for the main project
urlpatterns = [
    # Redirect root to the login page
    path('', RedirectView.as_view(url='/login/', permanent=True), name='index'),

    # Admin interface
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', user_views.register, name='register'),

    # Password reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # API endpoints (v1)
    path('api/v1/', include('patients.api.urls')),
    
    # Web interface
    path('', home, name='home'), 
    path('patients/', include('patients.urls')), 

    path('appointments/', include('appointments.urls', namespace='appointments')),
    path('pharmacy/', include('pharmacy.urls', namespace='pharmacy')),
]

# Debug configurations
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)