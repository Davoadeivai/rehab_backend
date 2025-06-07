from django.urls import path
from .views import (
    export_to_excel,
    export_to_pdf,
    patient_list,
    patient_create,
    patient_detail,
    patient_edit,
    patient_delete,
    prescription_create,
    prescription_list,
    prescription_detail,
    distribution_list,
    distribution_create,
    payment_list,
    payment_create,
    payment_detail,
    payment_edit,
    payment_delete,
    report_list,
    patient_search,
    inventory_view,  # Add this import
    UpdateInventoryView,  # Add this import if using class-based view
    financial_reports,
    patient_reports,
    prescription_reports,
    profile,
    settings,
    home,
    contact,
    faq,
    docs,
    support,
    feedback,
    drug_appointment_calendar,
    drug_appointments_json,
    create_drug_appointment,
    get_notifications
)

app_name = 'patients'

urlpatterns = [
    # Home
    path('', home, name='home'),
    
    # Patient paths
    path('patient_list/', patient_list, name='patient_list'),
    path('search/', patient_search, name='patient_search'),
    path('patient/create/', patient_create, name='patient_create'),
    path('patient/<int:pk>/', patient_detail, name='patient_detail'),
    path('patient/<int:pk>/edit/', patient_edit, name='patient_update'),
    path('patient/<int:pk>/delete/', patient_delete, name='patient_delete'),
    
    # Prescription paths
    path('prescriptions/', prescription_list, name='prescription_list'),
    path('prescription/create/', prescription_create, name='prescription_create'),
    path('prescription/<int:pk>/', prescription_detail, name='prescription_detail'),
    path('prescriptions/<int:pk>/update/', prescription_update, name='prescription_update'),
    
    # Medication distribution paths
    path('distributions/', distribution_list, name='distribution_list'),
    path('distribution/create/', distribution_create, name='distribution_create'),
    
    # Payment paths
    path('payments/', payment_list, name='payment_list'),
    path('payment/create/', payment_create, name='payment_create'),
    path('payment/<int:pk>/', payment_detail, name='payment_detail'),
    path('payment/<int:pk>/edit/', payment_edit, name='payment_update'),
    path('payment/<int:pk>/delete/', payment_delete, name='payment_delete'),
    
    # Report paths
    path('reports/', report_list, name='report_list'),
    path('financial-reports/', financial_reports, name='financial_reports'),
    path('patient-reports/', patient_reports, name='patient_reports'),
    path('prescription-reports/', prescription_reports, name='prescription_reports'),
    
    # Export paths
    path('export/excel/', export_to_excel, name='export_excel'),
    path('export/pdf/', export_to_pdf, name='export_pdf'),
    
    # Inventory paths (uncomment and fix these)
    path('inventory/', inventory_view, name='inventory_list'),
    path('inventory/<int:pk>/update/', UpdateInventoryView.as_view(), name='inventory_update'),
    
    # Profile and settings paths
    path('profile/', profile, name='profile'),
    path('settings/', settings, name='settings'),
    
    # Contact, FAQ, Docs, Support, Feedback paths
    path('contact/', contact, name='contact'),
    path('faq/', faq, name='faq'),
    path('docs/', docs, name='docs'),
    path('support/', support, name='support'),
    path('feedback/', feedback, name='feedback'),

    path('appointments/calendar/', drug_appointment_calendar, name='drug_appointment_calendar'),
    path('appointments/api/', drug_appointments_json, name='drug_appointments_json'),
    path('appointments/create/', create_drug_appointment, name='create_drug_appointment'),
    path('notifications/', get_notifications, name='get_notifications'),
]