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
    distribution_list,
    distribution_create,
    payment_list,
    payment_create,
    payment_detail,
    payment_edit,
    payment_delete,
    report_list,
)

app_name = 'patients'

urlpatterns = [
    # Web interface routes
    path('', patient_list, name='patient_list'),
    path('patient/create/', patient_create, name='patient_create'),
    path('patient/<int:pk>/', patient_detail, name='patient_detail'),
    path('patient/<int:pk>/edit/', patient_edit, name='patient_update'),
    path('patient/<int:pk>/delete/', patient_delete, name='patient_delete'),
    
    # Prescription routes
    path('prescriptions/', prescription_list, name='prescription_list'),
    path('prescription/create/', prescription_create, name='prescription_create'),
    
    # Distribution routes
    path('distributions/', distribution_list, name='distribution_list'),
    path('distribution/create/', distribution_create, name='distribution_create'),
    
    # Payment routes
    path('payments/', payment_list, name='payment_list'),
    path('payment/create/', payment_create, name='payment_create'),
    path('payment/<int:pk>/', payment_detail, name='payment_detail'),
    path('payment/<int:pk>/edit/', payment_edit, name='payment_update'),
    path('payment/<int:pk>/delete/', payment_delete, name='payment_delete'),
    
    # Report routes
    path('reports/', report_list, name='report_list'),
    
    # Export routes
    path('export/excel/', export_to_excel, name='export_excel'),
    path('export/pdf/', export_to_pdf, name='export_pdf'),
]