from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/', views.appointments_json, name='appointments_api'),
    path('create/', views.create_appointment, name='appointments_create'),
    path('detail/<int:pk>/', views.appointment_detail, name='appointment_detail'),
] 