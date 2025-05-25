from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AuthViewSet,
    PatientViewSet,
    export_to_excel,  # اضافه کردن view برای خروجی اکسل
    export_to_pdf,    # اضافه کردن view برای خروجی PDF
)

router = DefaultRouter()

# ثبت ViewSetها
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'patients', PatientViewSet, basename='patients')

urlpatterns = [
    path('', include(router.urls)),  # ViewSet‌ها
    path('export/excel/', export_to_excel, name='export_excel'),  # مسیر دانلود اکسل
    path('export/pdf/', export_to_pdf, name='export_pdf'),        # مسیر دانلود PDF
]