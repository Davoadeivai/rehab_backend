from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import routers

from .views import (
    AuthViewSet,
    PatientViewSet,
    MedicationTypeViewSet,
    PrescriptionViewSet,
    MedicationDistributionViewSet,
    PaymentViewSet,
    export_to_excel,  # اضافه کردن view برای خروجی اکسل
    export_to_pdf,    # اضافه کردن view برای خروجی PDF
)

class DefaultRouterWithAuth(DefaultRouter):
    def get_api_root_view(self, api_urls=None):
        api_root_dict = {}
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        api_root_dict.update({
            'login': 'auth-login',
            'register': 'auth-register',
            'export-excel': 'export_excel',
            'export-pdf': 'export_pdf',
            'medications': 'medication_types-list',
            'prescriptions': 'prescriptions-list',
            'distributions': 'medication_distributions-list',
            'payments': 'payments-list'
        })
        return self.APIRootView.as_view(api_root_dict=api_root_dict)

router = DefaultRouterWithAuth()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'medication-types', MedicationTypeViewSet, basename='medication_types')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescriptions')
router.register(r'medication-distributions', MedicationDistributionViewSet, basename='medication_distributions')
router.register(r'payments', PaymentViewSet, basename='payments')

# Let DefaultRouter handle the root API view
urlpatterns = router.urls + [
    path('export/excel/', export_to_excel, name='export_excel'),  # مسیر دانلود اکسل
    path('export/pdf/', export_to_pdf, name='export_pdf'),        # مسیر دانلود PDF
]