from django.urls import path, include
from rest_framework.routers import DefaultRouter
from patients.views import (
    AuthViewSet,
    PatientViewSet,
    MedicationTypeViewSet,
    PrescriptionViewSet,
    MedicationDistributionViewSet,
    PaymentViewSet,
    PatientListCreateAPIView,
    PatientRetrieveUpdateDestroyAPIView,
    patient_drug_quota_report,
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'medication-types', MedicationTypeViewSet, basename='medication_types')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescriptions')
router.register(r'medication-distributions', MedicationDistributionViewSet, basename='medication_distributions')
router.register(r'payments', PaymentViewSet, basename='payments')

# URL patterns for API endpoints
urlpatterns = router.urls + [
    # Additional API endpoints that don't use ViewSets
    path('patients/', PatientListCreateAPIView.as_view(), name='patient-list-create'),
    path('patients/<int:pk>/', PatientRetrieveUpdateDestroyAPIView.as_view(), name='patient-detail'),
]
urlpatterns += [
    path('patients/<int:patient_id>/drug-quota-report/', patient_drug_quota_report, name='patient_drug_quota_report'),
] 