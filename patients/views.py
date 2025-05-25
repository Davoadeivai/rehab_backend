from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from .models import Patient 
from openpyxl import Workbook
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from django.conf import settings    
from django.utils import timezone
from django.utils.html import strip_tags





 # MedicationInventory باید در models تعریف شود
from .serializers import (
    PatientSerializer,
    RegisterSerializer,
    LoginSerializer,
)
from .services.medication_summary import monthly_medication_summary

# -------------------------------
# Authentication API (Register & Login)
# -------------------------------

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            return Response({'error': 'نام کاربری یا رمز عبور اشتباه است'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# Patient, Family, Medication APIs
# -------------------------------

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


def export_to_excel(request):
    # ایجاد یک فایل اکسل جدید
    wb = Workbook()
    ws = wb.active
    ws.title = "لیست بیماران"
    
    # اضافه کردن هدر
    headers = [
        'شماره پرونده', 'نام', 'نام خانوادگی', 'کد ملی', 'تاریخ تولد',
        'جنسیت', 'شماره تلفن', 'آدرس', 'وضعیت تأهل', 'تحصیلات',
        'نوع ماده مصرفی', 'نوع درمان', 'مدت مصرف', 'تاریخ پذیرش', 'تاریخ خروج از درمان'
    ]
    ws.append(headers)
    
    # اضافه کردن داده‌ها
    patients = Patient.objects.all()
    for patient in patients:
        ws.append([
            patient.file_number,
            patient.first_name,
            patient.last_name,
            patient.national_code,
            patient.date_birth,
            patient.get_gender_display(),
            patient.phone_number,
            patient.address,
            patient.marital_status,
            patient.education,
            patient.drug_type,
            patient.treatment_type,
            patient.usage_duration,
            patient.admission_date,
            patient.treatment_withdrawal_date
        ])

    # تنظیم عرض ستون‌ها
    for column in ws.columns:
        max_length = 0
        column = list(column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column[0].column_letter].width = adjusted_width

    # ذخیره فایل
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=patients.xlsx'
    wb.save(response)
    return response

def export_to_pdf(request):
    # دریافت داده‌ها
    patients = Patient.objects.all()
    
    # ایجاد HTML
    html_string = render_to_string('patients/pdf_template.html', {'patients': patients})
    
    # تبدیل HTML به PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="patients.pdf"'
    
    # ایجاد PDF
    pdf = pisa.CreatePDF(
        html_string,
        dest=response,
        encoding='UTF-8'
    )
    
    if not pdf.err:
        return response
    return HttpResponse('خطا در ایجاد PDF')
