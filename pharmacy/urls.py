from django.urls import path
from .views import (
    # Drug Views
    DrugListView, DrugCreateView, DrugUpdateView, DrugDeleteView, DrugDetailView,

    # Supplier Views
    SupplierListView, SupplierCreateView, SupplierUpdateView, SupplierDeleteView,

    # Purchase Views
    DrugPurchaseListView, DrugPurchaseCreateView, DrugPurchaseUpdateView,
    DrugPurchaseDeleteView, DrugPurchaseDetailView, DrugPurchaseExcelExportView,

    # Sale Views
    DrugSaleListView, DrugSaleCreateView, DrugSaleUpdateView, DrugSaleDeleteView,
    DrugSaleByPrescriptionView, DrugSaleReportView,

    # Inventory & Reports
    DrugInventoryReportView, DrugInventoryExcelExportView,

    # Dashboard & Analytics
    PharmacyDashboardView, PharmacyAnalyticsView,
)

app_name = 'pharmacy'

urlpatterns = [

    # ------------------------
    #        DRUGS
    # ------------------------
    path('drugs/', DrugListView.as_view(), name='drug_list'),
    path('drugs/add/', DrugCreateView.as_view(), name='drug_add'),
    path('drugs/<int:pk>/edit/', DrugUpdateView.as_view(), name='drug_edit'),
    path('drugs/<int:pk>/delete/', DrugDeleteView.as_view(), name='drug_delete'),
    path('drugs/<int:pk>/', DrugDetailView.as_view(), name='drug_detail'),

    # ------------------------
    #       SUPPLIERS
    # ------------------------
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', SupplierCreateView.as_view(), name='supplier_add'),
    path('suppliers/<int:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier_delete'),

    # ------------------------
    #       PURCHASES
    # ------------------------
    path('purchases/', DrugPurchaseListView.as_view(), name='purchase_list'),
    path('purchases/add/', DrugPurchaseCreateView.as_view(), name='purchase_add'),
    path('purchases/<int:pk>/edit/', DrugPurchaseUpdateView.as_view(), name='purchase_edit'),
    path('purchases/<int:pk>/delete/', DrugPurchaseDeleteView.as_view(), name='purchase_delete'),
    path('purchases/<int:pk>/', DrugPurchaseDetailView.as_view(), name='purchase_detail'),
    path('purchases/export/excel/', DrugPurchaseExcelExportView.as_view(), name='purchase_export_excel'),

    # ------------------------
    #          SALES
    # ------------------------
    path('sales/', DrugSaleListView.as_view(), name='sale_list'),
    path('sales/add/', DrugSaleCreateView.as_view(), name='sale_add'),
    path('sales/<int:pk>/edit/', DrugSaleUpdateView.as_view(), name='sale_edit'),
    path('sales/<int:pk>/delete/', DrugSaleDeleteView.as_view(), name='sale_delete'),
    path('sales/by-prescription/', DrugSaleByPrescriptionView.as_view(), name='sale_by_prescription'),
    path('sales/report/', DrugSaleReportView.as_view(), name='sale_report'),

    # ------------------------
    #       INVENTORY
    # ------------------------
    path('inventory-report/', DrugInventoryReportView.as_view(), name='inventory_report'),
    path('inventory-report/excel/', DrugInventoryExcelExportView.as_view(), name='inventory_report_excel'),

    # ------------------------
    # Dashboard & Analytics
    # ------------------------
    path('dashboard/', PharmacyDashboardView.as_view(), name='dashboard'),
    path('analytics/', PharmacyAnalyticsView.as_view(), name='pharmacy_analytics'),
]
