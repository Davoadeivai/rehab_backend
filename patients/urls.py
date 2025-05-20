from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, FamilyViewSet, MedicationViewSet,generate_patient_pdf, login_view,dashboard_view,logout_view,patient_create,patient_list,patient_detail_view,patient_edit_view, patient_delete_view,add_family, add_medication
from django.contrib.auth import views as auth_views






router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'families', FamilyViewSet)
router.register(r'medications', MedicationViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # path('login/', lambda request: HttpResponse("Login Page"), name='login'),

    path('patient/<int:pk>/pdf/', generate_patient_pdf, name='generate_patient_pdf'),
    path('login/',login_view, name='login'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('patient/create/',patient_create, name='patient_create'),
    path('patient/list/',patient_list, name='patient_list'),
    path('patient/<int:pk>/', patient_detail_view, name='patient_detail_view'),
    path('patient/<int:pk>/edit/', patient_edit_view, name='patient_edit_view'),
    path('patient/<int:pk>/delete/', patient_delete_view, name='patient_delete_view'),
    path('patient/<int:patient_id>/add_family/', add_family, name='add_family'),
    path('patient/<int:patient_id>/add_medication/', add_medication, name='add_medication'),
    
]