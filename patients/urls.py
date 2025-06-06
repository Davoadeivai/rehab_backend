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
    patient_search,
    inventory_list,
    inventory_view,
    UpdateInventoryView
)

app_name = 'patients'

urlpatterns = [
    # Patient paths
    path('', patient_list, name='patient_list'),
    path('search/', patient_search, name='patient_search'),
    path('patient/create/', patient_create, name='patient_create'),
    path('patient/<int:pk>/', patient_detail, name='patient_detail'),
    path('patient/<int:pk>/edit/', patient_edit, name='patient_edit'),
    path('patient/<int:pk>/delete/', patient_delete, name='patient_delete'),
    
    # Prescription paths
    path('prescriptions/', prescription_list, name='prescription_list'),
    path('prescription/create/', prescription_create, name='prescription_create'),
    
    # Medication distribution paths
    path('distributions/', distribution_list, name='distribution_list'),
    path('distribution/create/', distribution_create, name='distribution_create'),
    
    # Payment paths
    path('payments/', payment_list, name='payment_list'),
    path('payment/create/', payment_create, name='payment_create'),
    path('payment/<int:pk>/', payment_detail, name='payment_detail'),
    path('payment/<int:pk>/edit/', payment_edit, name='payment_edit'),
    path('payment/<int:pk>/delete/', payment_delete, name='payment_delete'),
    
    # Report paths
    path('reports/', report_list, name='report_list'),
    
    # Export paths
    path('export/excel/', export_to_excel, name='export_excel'),
    path('export/pdf/', export_to_pdf, name='export_pdf'),
    
    # Inventory paths (uncomment and fix these)
    path('inventory/', inventory_list, name='inventory_list'), # Changed from inventory_view
    path('inventory/<int:pk>/update/', UpdateInventoryView.as_view(), name='inventory_update'),
]