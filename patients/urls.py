from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, FamilyViewSet, MedicationViewSet

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'families', FamilyViewSet)
router.register(r'medications', MedicationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]