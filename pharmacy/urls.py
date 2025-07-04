from django.urls import path
from .views import (
    DrugListView, DrugCreateView, DrugUpdateView, DrugDeleteView,
    SupplierListView, SupplierCreateView, SupplierUpdateView, SupplierDeleteView,
    DrugPurchaseListView, DrugPurchaseCreateView, DrugPurchaseUpdateView, DrugPurchaseDeleteView,
    DrugSaleListView, DrugSaleUpdateView, DrugSaleDeleteView,
    DrugInventoryReportView, DrugSaleByPrescriptionView, PharmacyDashboardView, DrugInventoryExcelExportView,
    DrugInventoryPDFExportView
)

app_name = 'pharmacy'

urlpatterns = [
    path('drugs/', DrugListView.as_view(), name='drug_list'),
    path('drugs/add/', DrugCreateView.as_view(), name='drug_add'),
    path('drugs/<int:pk>/edit/', DrugUpdateView.as_view(), name='drug_edit'),
    path('drugs/<int:pk>/delete/', DrugDeleteView.as_view(), name='drug_delete'),
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', SupplierCreateView.as_view(), name='supplier_add'),
    path('suppliers/<int:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),
    path('purchases/', DrugPurchaseListView.as_view(), name='purchase_list'),
    path('purchases/add/', DrugPurchaseCreateView.as_view(), name='purchase_add'),
    path('purchases/<int:pk>/edit/', DrugPurchaseUpdateView.as_view(), name='purchase_edit'),
    path('purchases/<int:pk>/delete/', DrugPurchaseDeleteView.as_view(), name='purchase_delete'),
    path('sales/', DrugSaleListView.as_view(), name='sale_list'),
    path('sales/<int:pk>/edit/', DrugSaleUpdateView.as_view(), name='sale_edit'),
    path('sales/<int:pk>/delete/', DrugSaleDeleteView.as_view(), name='sale_delete'),
    path('sales/by-prescription/', DrugSaleByPrescriptionView.as_view(), name='sale_by_prescription'),
    path('inventory-report/', DrugInventoryReportView.as_view(), name='inventory_report'),
    path('inventory-report/excel/', DrugInventoryExcelExportView.as_view(), name='inventory_report_excel'),
    path('inventory-report/pdf/', DrugInventoryPDFExportView.as_view(), name='inventory_report_pdf'),
    path('dashboard/', PharmacyDashboardView.as_view(), name='dashboard'),
] 