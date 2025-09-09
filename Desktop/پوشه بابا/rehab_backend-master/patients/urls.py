from django.urls import path
from patients.dashboard import admin_dashboard
import patients.views as patient_views

app_name = 'patients'

urlpatterns = [
    # Admin Dashboard
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # Home
    path('', patient_views.home, name='home'),
    
    # Patient paths
    path('', patient_views.patient_list, name='patient_list'),
    path('search/', patient_views.patient_search, name='patient_search'),
    path('patient/create/', patient_views.patient_create, name='patient_create'),
    path('patient/<str:pk>/', patient_views.patient_detail, name='patient_detail'),
    path('patient/<str:pk>/edit/', patient_views.patient_edit, name='patient_update'),
    path('patient/<str:pk>/delete/', patient_views.patient_delete, name='patient_delete'),
    
    # Medication paths
    path('medications/', patient_views.medication_list, name='medication_list'),
    path('medications/create/', patient_views.medication_create, name='medication_create'),
    path('medication-administrations/<int:pk>/delete/', patient_views.medication_administration_delete, name='medication_administration_delete'),

    path('dashboard/', patient_views.dashboard, name='dashboard'),

    # URLs for Services
    path('services/', patient_views.service_list, name='service_list'),
    path('service-transactions/create/', patient_views.service_transaction_create, name='service_transaction_create'),
    path('medication_administration/list/', patient_views.medication_administration_list, name='medication_administration_list'),
    
    # Prescription paths
    path('prescriptions/', patient_views.prescription_list, name='prescription_list'),
    path('prescription/create/', patient_views.prescription_create, name='prescription_create'),
    path('prescription/<int:pk>/', patient_views.prescription_detail, name='prescription_detail'),
    path('prescriptions/<int:pk>/update/', patient_views.prescription_update, name='prescription_update'),
    path('prescriptions/<int:pk>/delete/', patient_views.prescription_delete, name='prescription_delete'),
    
    # Medication distribution paths
    path('distributions/', patient_views.distribution_list, name='distribution_list'),
    path('distribution/create/', patient_views.distribution_create, name='distribution_create'),
    
    # Payment paths
    path('payments/', patient_views.payment_list, name='payment_list'),
    path('payment/create/', patient_views.payment_create, name='payment_create'),
    path('payment/<int:pk>/', patient_views.payment_detail, name='payment_detail'),
    path('payment/<int:pk>/edit/', patient_views.payment_edit, name='payment_update'),
    path('payment/<int:pk>/delete/', patient_views.payment_delete, name='payment_delete'),
    path('payment/<int:pk>/pay/', patient_views.initiate_pos_payment, name='initiate_pos_payment'),
    
    # Report paths
    path('reports/', patient_views.report_list, name='report_list'),
    path('financial-reports/', patient_views.financial_reports, name='financial_reports'),
    path('patient-reports/', patient_views.patient_reports, name='patient_reports'),
    path('prescription-reports/', patient_views.prescription_reports, name='prescription_reports'),
    
    # Export paths
    path('export/excel/', patient_views.export_to_excel, name='export_excel'),
    path('export/pdf/', patient_views.export_to_pdf, name='export_pdf'),
    
    # Inventory paths (uncomment and fix these)
    path('inventory/', patient_views.inventory_view, name='inventory_list'),
    path('inventory/<int:pk>/update/', patient_views.UpdateInventoryView.as_view(), name='inventory_update'),
    path('quota/', patient_views.inventory_view, name='quota_list'),
    path('alerts/', patient_views.inventory_view, name='alert_list'),
    path('transactions/', patient_views.inventory_view, name='transaction_list'),
    
    # Profile and settings paths
    path('profile/', patient_views.profile, name='profile'),
    path('settings/', patient_views.settings, name='settings'),
    
    # Contact, FAQ, Docs, Support, Feedback paths
    path('contact/', patient_views.contact, name='contact'),
    path('faq/', patient_views.faq, name='faq'),
    path('docs/', patient_views.docs, name='docs'),
    path('support/', patient_views.support, name='support'),
    path('feedback/', patient_views.feedback, name='feedback'),

    # API endpoints
    path('notifications/', patient_views.get_notifications, name='get_notifications'),
    path('api/medication/<int:medication_id>/details/', patient_views.get_medication_details, name='get_medication_details'),
    path('api/calculate-end-date/', patient_views.calculate_end_date, name='calculate_end_date'),

    path('appointments/calendar/', patient_views.drug_appointment_calendar, name='drug_appointment_calendar'),
    path('appointments/api/', patient_views.drug_appointments_json, name='drug_appointments_json'),
    path('appointments/create/', patient_views.create_drug_appointment, name='create_drug_appointment'),
]