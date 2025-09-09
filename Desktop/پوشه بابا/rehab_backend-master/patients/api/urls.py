from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthViewSet,
    PatientViewSet,
    MedicationTypeViewSet,
    PrescriptionViewSet,
    MedicationDistributionViewSet,
    PaymentViewSet,
    PatientListCreateAPIView,
    PatientRetrieveUpdateDestroyAPIView,
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
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional API endpoints
    path('patients/', PatientListCreateAPIView.as_view(), name='patient-list-create'),
    path('patients/search/', PatientViewSet.as_view({'get': 'search'}), name='patient-search'),
    path('patients/<int:pk>/', PatientRetrieveUpdateDestroyAPIView.as_view(), name='patient-detail'),
] 