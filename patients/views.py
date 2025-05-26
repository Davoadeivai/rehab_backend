from django.contrib.auth import authenticate
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.http import HttpResponse
from .models import Patient, MedicationType, Prescription, MedicationDistribution, Payment
from openpyxl import Workbook
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from django.conf import settings    
from django.utils import timezone
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Count, Sum
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
from django.db.models import Q
import jdatetime
from .utils import format_jalali_date, format_jalali_full_date, format_number

from .serializers import (
    PatientSerializer,
    RegisterSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    MedicationTypeSerializer,
    PrescriptionSerializer,
    MedicationDistributionSerializer,
    PaymentSerializer,
)
from .services.medication_summary import monthly_medication_summary

# -------------------------------
# Authentication API (Register & Login)
# -------------------------------

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer  # Default serializer

    @action(detail=False, methods=['post'], url_path='login', url_name='login')
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

    @action(detail=False, methods=['post'], url_path='register', url_name='register')
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='password-reset', url_name='password_reset')
    def password_reset(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link (you'll need to modify this for your frontend URL)
            reset_url = f"http://your-frontend-url/reset-password/{uid}/{token}/"
            
            # Send email
            send_mail(
                'بازیابی رمز عبور',
                f'برای بازیابی رمز عبور خود روی لینک زیر کلیک کنید:\n\n{reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({"detail": "ایمیل بازیابی رمز عبور ارسال شد."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='password-reset-confirm', url_name='password_reset_confirm')
    def password_reset_confirm(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uidb64']))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({"detail": "لینک نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

            if default_token_generator.check_token(user, serializer.validated_data['token']):
                user.set_password(serializer.validated_data['password'])
                user.save()
                return Response({"detail": "رمز عبور با موفقیت تغییر کرد."})
            return Response({"detail": "توکن نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = []

    def get_queryset(self):
        """
        سیستم جستجوی پیشرفته برای بیماران
        """
        queryset = Patient.objects.all()
        
        # جستجوی عمومی
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(national_code__icontains=search) |
                Q(file_number__icontains=search)
            )

        # فیلترهای دقیق
        filters = {
            'gender': 'gender',
            'marital_status': 'marital_status',
            'education': 'education',
            'treatment_type': 'treatment_type',
            'drug_type': 'drug_type',
        }
        
        for param, field in filters.items():
            value = self.request.query_params.get(param, None)
            if value:
                queryset = queryset.filter(**{field: value})

        # فیلتر تاریخ
        admission_after = self.request.query_params.get('admission_after', None)
        admission_before = self.request.query_params.get('admission_before', None)
        
        if admission_after:
            queryset = queryset.filter(admission_date__gte=admission_after)
        if admission_before:
            queryset = queryset.filter(admission_date__lte=admission_before)

        # فیلتر وضعیت درمان
        treatment_status = self.request.query_params.get('treatment_status', None)
        if treatment_status:
            if treatment_status == 'active':
                queryset = queryset.filter(treatment_withdrawal_date__isnull=True)
            elif treatment_status == 'completed':
                queryset = queryset.filter(treatment_withdrawal_date__isnull=False)

        # مرتب‌سازی
        sort_by = self.request.query_params.get('sort_by', '-admission_date')
        if sort_by:
            queryset = queryset.order_by(sort_by)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        ایجاد یک بیمار جدید
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"detail": "بیمار با موفقیت ثبت شد", "data": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        """
        به‌روزرسانی اطلاعات بیمار
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"detail": "اطلاعات بیمار با موفقیت به‌روز شد", "data": serializer.data}
        )

    def destroy(self, request, *args, **kwargs):
        """
        حذف بیمار
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "بیمار با موفقیت حذف شد"},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['get'])
    def full_details(self, request, pk=None):
        """
        نمایش جزئیات کامل یک بیمار
        """
        patient = self.get_object()
        serializer = self.get_serializer(patient)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active_patients(self, request):
        """
        لیست بیمارانی که هنوز در حال درمان هستند
        """
        active_patients = self.get_queryset().filter(treatment_withdrawal_date__isnull=True)
        serializer = self.get_serializer(active_patients, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        آمار پیشرفته بیماران
        """
        queryset = self.get_queryset()
        current_date = jdatetime.datetime.now().date()
        
        # آمار کلی
        total_patients = queryset.count()
        active_patients = queryset.filter(treatment_withdrawal_date__isnull=True).count()
        completed_treatments = queryset.filter(treatment_withdrawal_date__isnull=False).count()
        
        # آمار جنسیتی
        gender_stats = queryset.values('gender').annotate(count=Count('gender'))
        
        # آمار نوع درمان
        treatment_stats = queryset.values('treatment_type').annotate(count=Count('treatment_type'))
        
        # آمار نوع مواد مصرفی
        drug_stats = queryset.values('drug_type').annotate(count=Count('drug_type'))
        
        # میانگین مدت درمان برای درمان‌های تکمیل شده
        completed_treatments_qs = queryset.filter(
            treatment_withdrawal_date__isnull=False,
            admission_date__isnull=False
        )
        
        avg_treatment_duration = 0
        if completed_treatments_qs.exists():
            total_days = sum(
                (patient.treatment_withdrawal_date - patient.admission_date).days
                for patient in completed_treatments_qs
            )
            avg_treatment_duration = total_days / completed_treatments_qs.count()

        return Response({
            'total_statistics': {
                'total_patients': total_patients,
                'active_patients': active_patients,
                'completed_treatments': completed_treatments,
                'avg_treatment_duration': round(avg_treatment_duration, 1)
            },
            'gender_statistics': gender_stats,
            'treatment_type_statistics': treatment_stats,
            'drug_type_statistics': drug_stats,
        })

    @action(detail=True, methods=['get'])
    def comprehensive_report(self, request, pk=None):
        """
        گزارش جامع از تمام فعالیت‌های یک بیمار شامل:
        - اطلاعات شخصی
        - نسخه‌های دارویی
        - توزیع داروها
        - پرداخت‌ها
        - آمار کلی
        """
        patient = self.get_object()
        
        # اطلاعات شخصی بیمار
        patient_data = self.get_serializer(patient).data
        
        # نسخه‌های دارویی
        prescriptions = Prescription.objects.filter(patient=patient).order_by('-start_date')
        prescription_data = PrescriptionSerializer(prescriptions, many=True).data
        
        # توزیع داروها
        distributions = MedicationDistribution.objects.filter(
            prescription__patient=patient
        ).order_by('-distribution_date')
        distribution_data = MedicationDistributionSerializer(distributions, many=True).data
        
        # پرداخت‌ها
        payments = Payment.objects.filter(patient=patient).order_by('-payment_date')
        payment_data = PaymentSerializer(payments, many=True).data
        
        # آمار کلی
        total_prescribed = prescriptions.aggregate(
            total=Sum('total_prescribed')
        )['total'] or 0
        
        total_distributed = distributions.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_payments = payments.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # محاسبه مدت درمان
        if patient.admission_date:
            if patient.treatment_withdrawal_date:
                treatment_duration = (patient.treatment_withdrawal_date - patient.admission_date).days
                status = "اتمام درمان"
            else:
                current_date = jdatetime.datetime.now().date()
                treatment_duration = (current_date - patient.admission_date).days
                status = "در حال درمان"
        else:
            treatment_duration = 0
            status = "نامشخص"
        
        # آمار پرداخت‌ها بر اساس نوع
        payment_stats = payments.values('payment_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        # تبدیل تاریخ‌ها به فرمت فارسی
        jalali_dates = {
            'admission_date': format_jalali_full_date(patient.admission_date),
            'treatment_withdrawal_date': format_jalali_full_date(patient.treatment_withdrawal_date),
            'last_prescription': format_jalali_full_date(prescriptions.first().start_date) if prescriptions.exists() else '',
            'last_distribution': format_jalali_full_date(distributions.first().distribution_date) if distributions.exists() else '',
            'last_payment': format_jalali_full_date(payments.first().payment_date) if payments.exists() else '',
        }
        
        # آمار ماهانه پرداخت‌ها
        monthly_payments = payments.extra(
            select={'month': "EXTRACT(month FROM payment_date)"}
        ).values('month').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')
        
        # تبدیل شماره ماه به نام فارسی ماه
        persian_months = {
            1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
            4: 'تیر', 5: 'مرداد', 6: 'شهریور',
            7: 'مهر', 8: 'آبان', 9: 'آذر',
            10: 'دی', 11: 'بهمن', 12: 'اسفند'
        }
        
        monthly_payment_stats = [
            {
                'month': persian_months.get(item['month'], str(item['month'])),
                'total': item['total'],
                'count': item['count'],
                'total_display': "{:,}".format(item['total'])
            }
            for item in monthly_payments
        ]
        
        return Response({
            'patient_info': patient_data,
            'treatment_status': {
                'status': status,
                'duration_days': treatment_duration,
                'important_dates': jalali_dates
            },
            'medication_summary': {
                'total_prescribed': total_prescribed,
                'total_distributed': total_distributed,
                'remaining': total_prescribed - total_distributed,
                'prescriptions_count': prescriptions.count(),
                'distributions_count': distributions.count()
            },
            'financial_summary': {
                'total_payments': total_payments,
                'total_payments_display': "{:,}".format(total_payments),
                'payment_stats': payment_stats,
                'monthly_stats': monthly_payment_stats,
                'payments_count': payments.count()
            },
            'prescriptions': prescription_data,
            'distributions': distribution_data,
            'payments': payment_data
        })

def export_to_excel(request):
    """
    خروجی اکسل از تمام فعالیت‌های بیماران
    """
    wb = Workbook()
    
    # ایجاد شیت‌های مختلف
    ws_patients = wb.active
    ws_patients.title = "لیست بیماران"
    ws_prescriptions = wb.create_sheet("نسخه‌های دارویی")
    ws_distributions = wb.create_sheet("توزیع دارو")
    ws_payments = wb.create_sheet("پرداخت‌ها")
    ws_stats = wb.create_sheet("آمار و تحلیل")
    
    # تنظیم استایل‌های سلول‌ها
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(name='B Nazanin', size=12, bold=True, color="FFFFFF")
    normal_font = Font(name='B Nazanin', size=11)
    centered_alignment = Alignment(horizontal='center', vertical='center')
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # === شیت بیماران ===
    headers_patients = [
        'شماره پرونده', 'نام', 'نام خانوادگی', 'کد ملی', 'تاریخ تولد',
        'جنسیت', 'شماره تلفن', 'آدرس', 'وضعیت تأهل', 'تحصیلات',
        'نوع ماده مصرفی', 'نوع درمان', 'مدت مصرف', 'تاریخ پذیرش', 'تاریخ خروج از درمان',
        'مدت زمان درمان (روز)', 'وضعیت فعلی'
    ]
    
    # اعمال هدرها در شیت بیماران
    for col, header in enumerate(headers_patients, 1):
        cell = ws_patients.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = centered_alignment
        cell.border = border
        ws_patients.column_dimensions[get_column_letter(col)].width = 15

    # === شیت نسخه‌ها ===
    headers_prescriptions = [
        'شماره پرونده بیمار', 'نام و نام خانوادگی', 'نوع دارو', 'دوز روزانه',
        'مدت درمان', 'تاریخ شروع', 'تاریخ پایان', 'مقدار کل تجویز شده',
        'یادداشت', 'تاریخ ثبت'
    ]
    
    for col, header in enumerate(headers_prescriptions, 1):
        cell = ws_prescriptions.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = centered_alignment
        cell.border = border
        ws_prescriptions.column_dimensions[get_column_letter(col)].width = 15

    # === شیت توزیع دارو ===
    headers_distributions = [
        'شماره پرونده بیمار', 'نام و نام خانوادگی', 'نوع دارو', 'تاریخ توزیع',
        'مقدار', 'باقی‌مانده', 'یادداشت', 'تاریخ ثبت'
    ]
    
    for col, header in enumerate(headers_distributions, 1):
        cell = ws_distributions.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = centered_alignment
        cell.border = border
        ws_distributions.column_dimensions[get_column_letter(col)].width = 15

    # === شیت پرداخت‌ها ===
    headers_payments = [
        'شماره پرونده بیمار', 'نام و نام خانوادگی', 'تاریخ پرداخت',
        'مبلغ', 'نوع پرداخت', 'توضیحات', 'تاریخ ثبت'
    ]
    
    for col, header in enumerate(headers_payments, 1):
        cell = ws_payments.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = centered_alignment
        cell.border = border
        ws_payments.column_dimensions[get_column_letter(col)].width = 15

    # دریافت داده‌ها
    patients = Patient.objects.all().order_by('-admission_date')
    prescriptions = Prescription.objects.all().order_by('-start_date')
    distributions = MedicationDistribution.objects.all().order_by('-distribution_date')
    payments = Payment.objects.all().order_by('-payment_date')
    
    current_date = jdatetime.datetime.now().date()
    
    # پر کردن داده‌های بیماران
    for idx, patient in enumerate(patients, 2):
        # محاسبه مدت زمان درمان
        if patient.admission_date:
            if patient.treatment_withdrawal_date:
                treatment_duration = (patient.treatment_withdrawal_date - patient.admission_date).days
                status = "اتمام درمان"
            else:
                treatment_duration = (current_date - patient.admission_date).days
                status = "در حال درمان"
        else:
            treatment_duration = 0
            status = "نامشخص"

        row_data = [
            patient.file_number,
            patient.first_name,
            patient.last_name,
            patient.national_code,
            format_jalali_date(patient.date_birth) if patient.date_birth else '',
            patient.get_gender_display() if patient.gender else '',
            patient.phone_number,
            patient.address,
            patient.marital_status,
            patient.education,
            patient.drug_type,
            patient.treatment_type,
            patient.usage_duration,
            format_jalali_date(patient.admission_date) if patient.admission_date else '',
            format_jalali_date(patient.treatment_withdrawal_date) if patient.treatment_withdrawal_date else '',
            treatment_duration,
            status
        ]

        for col, value in enumerate(row_data, 1):
            cell = ws_patients.cell(row=idx, column=col, value=value)
            cell.font = normal_font
            cell.alignment = centered_alignment
            cell.border = border

    # پر کردن داده‌های نسخه‌ها
    for idx, prescription in enumerate(prescriptions, 2):
        row_data = [
            prescription.patient.file_number,
            f"{prescription.patient.first_name} {prescription.patient.last_name}",
            prescription.medication_type.name,
            prescription.daily_dose,
            prescription.treatment_duration,
            format_jalali_date(prescription.start_date),
            format_jalali_date(prescription.end_date),
            prescription.total_prescribed,
            prescription.notes,
            format_jalali_date(prescription.created_at, include_time=True)
        ]

        for col, value in enumerate(row_data, 1):
            cell = ws_prescriptions.cell(row=idx, column=col, value=value)
            cell.font = normal_font
            cell.alignment = centered_alignment
            cell.border = border

    # پر کردن داده‌های توزیع دارو
    for idx, distribution in enumerate(distributions, 2):
        row_data = [
            distribution.prescription.patient.file_number,
            f"{distribution.prescription.patient.first_name} {distribution.prescription.patient.last_name}",
            distribution.prescription.medication_type.name,
            format_jalali_date(distribution.distribution_date),
            distribution.amount,
            distribution.remaining,
            distribution.notes,
            format_jalali_date(distribution.created_at, include_time=True)
        ]

        for col, value in enumerate(row_data, 1):
            cell = ws_distributions.cell(row=idx, column=col, value=value)
            cell.font = normal_font
            cell.alignment = centered_alignment
            cell.border = border

    # پر کردن داده‌های پرداخت‌ها
    for idx, payment in enumerate(payments, 2):
        row_data = [
            payment.patient.file_number,
            f"{payment.patient.first_name} {payment.patient.last_name}",
            format_jalali_date(payment.payment_date),
            "{:,}".format(payment.amount),
            payment.get_payment_type_display(),
            payment.description,
            format_jalali_date(payment.created_at, include_time=True)
        ]

        for col, value in enumerate(row_data, 1):
            cell = ws_payments.cell(row=idx, column=col, value=value)
            cell.font = normal_font
            cell.alignment = centered_alignment
            cell.border = border

    # آمار و تحلیل در شیت آخر
    stats_headers = [
        ['آمار کلی بیماران', ''],
        ['تعداد کل بیماران', patients.count()],
        ['بیماران فعال', patients.filter(treatment_withdrawal_date__isnull=True).count()],
        ['بیماران با درمان تکمیل شده', patients.filter(treatment_withdrawal_date__isnull=False).count()],
        ['', ''],
        ['آمار مالی', ''],
        ['مجموع پرداخت‌ها', "{:,}".format(payments.aggregate(total=Sum('amount'))['total'] or 0)],
        ['تعداد تراکنش‌ها', payments.count()],
        ['', ''],
        ['آمار دارویی', ''],
        ['تعداد کل نسخه‌ها', prescriptions.count()],
        ['تعداد کل توزیع دارو', distributions.count()],
    ]

    for row, (label, value) in enumerate(stats_headers, 1):
        cell = ws_stats.cell(row=row, column=1, value=label)
        cell.font = header_font if row in [1, 6, 10] else normal_font
        cell.alignment = centered_alignment
        cell.border = border
        
        cell = ws_stats.cell(row=row, column=2, value=value)
        cell.font = normal_font
        cell.alignment = centered_alignment
        cell.border = border

    ws_stats.column_dimensions['A'].width = 30
    ws_stats.column_dimensions['B'].width = 15

    # ذخیره فایل
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=patients_full_report_{current_date.strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response

def export_to_pdf(request):
    """
    خروجی PDF از تمام فعالیت‌های بیماران
    """
    # دریافت داده‌ها
    patients = Patient.objects.all().order_by('-admission_date')
    current_date = jdatetime.datetime.now().date()
    
    # تهیه داده‌ها برای هر بیمار
    patients_data = []
    for patient in patients:
        # دریافت نسخه‌ها
        prescriptions = Prescription.objects.filter(patient=patient).order_by('-start_date')
        formatted_prescriptions = []
        for prescription in prescriptions:
            formatted_prescription = {
                'medication_type': prescription.medication_type,
                'daily_dose': prescription.daily_dose,
                'start_date': format_jalali_date(prescription.start_date),
                'end_date': format_jalali_date(prescription.end_date),
                'total_prescribed': prescription.total_prescribed,
                'notes': prescription.notes
            }
            formatted_prescriptions.append(formatted_prescription)
        
        # دریافت توزیع داروها
        distributions = MedicationDistribution.objects.filter(
            prescription__patient=patient
        ).order_by('-distribution_date')
        formatted_distributions = []
        for distribution in distributions:
            formatted_distribution = {
                'distribution_date': format_jalali_date(distribution.distribution_date),
                'prescription': distribution.prescription,
                'amount': distribution.amount,
                'remaining': distribution.remaining,
                'notes': distribution.notes
            }
            formatted_distributions.append(formatted_distribution)
        
        # دریافت پرداخت‌ها
        payments = Payment.objects.filter(patient=patient).order_by('-payment_date')
        total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        # فرمت‌بندی پرداخت‌ها
        formatted_payments = []
        for payment in payments:
            formatted_payment = {
                'payment_date': format_jalali_date(payment.payment_date),
                'amount': format_number(payment.amount),
                'payment_type': payment.get_payment_type_display(),
                'description': payment.description
            }
            formatted_payments.append(formatted_payment)
        
        # محاسبه مدت درمان
        if patient.admission_date:
            if patient.treatment_withdrawal_date:
                treatment_duration = (patient.treatment_withdrawal_date - patient.admission_date).days
                status = "اتمام درمان"
            else:
                treatment_duration = (current_date - patient.admission_date).days
                status = "در حال درمان"
        else:
            treatment_duration = 0
            status = "نامشخص"
        
        # جمع‌آوری اطلاعات بیمار
        patient_info = {
            'patient': patient,
            'treatment_status': status,
            'treatment_duration': treatment_duration,
            'prescriptions': formatted_prescriptions,
            'distributions': formatted_distributions,
            'payments': formatted_payments,
            'total_payments': format_number(total_payments),
            'formatted_dates': {
                'date_birth': format_jalali_full_date(patient.date_birth),
                'admission_date': format_jalali_full_date(patient.admission_date),
                'treatment_withdrawal_date': format_jalali_full_date(patient.treatment_withdrawal_date)
            }
        }
        patients_data.append(patient_info)
    
    # ایجاد HTML
    html_string = render_to_string('patients/pdf_report_template.html', {
        'patients_data': patients_data,
        'current_date': format_jalali_full_date(current_date),
        'total_patients': format_number(patients.count()),
        'active_patients': format_number(patients.filter(treatment_withdrawal_date__isnull=True).count()),
        'completed_patients': format_number(patients.filter(treatment_withdrawal_date__isnull=False).count())
    })
    
    # تبدیل HTML به PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=patients_full_report_{current_date.strftime("%Y%m%d")}.pdf'
    
    # ایجاد PDF
    pisa_status = pisa.CreatePDF(
        html_string,
        dest=response,
        encoding='UTF-8'
    )
    
    if pisa_status.err:
        return HttpResponse('خطا در ایجاد PDF')
    
    return response

class MedicationTypeViewSet(viewsets.ModelViewSet):
    queryset = MedicationType.objects.all()
    serializer_class = MedicationTypeSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = MedicationType.objects.all()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = Prescription.objects.all()
        
        # فیلتر بر اساس بیمار
        patient_id = self.request.query_params.get('patient', None)
        if patient_id:
            queryset = queryset.filter(patient__file_number=patient_id)
        
        # فیلتر بر اساس نوع دارو
        medication_type = self.request.query_params.get('medication_type', None)
        if medication_type:
            queryset = queryset.filter(medication_type_id=medication_type)
        
        # فیلتر بر اساس تاریخ
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        return queryset

    @action(detail=True, methods=['get'])
    def remaining_medication(self, request, pk=None):
        """محاسبه داروی باقی‌مانده برای یک نسخه"""
        prescription = self.get_object()
        total_distributed = MedicationDistribution.objects.filter(
            prescription=prescription
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        remaining = prescription.total_prescribed - total_distributed
        
        return Response({
            'total_prescribed': prescription.total_prescribed,
            'total_distributed': total_distributed,
            'remaining': remaining
        })

class MedicationDistributionViewSet(viewsets.ModelViewSet):
    queryset = MedicationDistribution.objects.all()
    serializer_class = MedicationDistributionSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = MedicationDistribution.objects.all()
        
        # فیلتر بر اساس نسخه
        prescription_id = self.request.query_params.get('prescription', None)
        if prescription_id:
            queryset = queryset.filter(prescription_id=prescription_id)
        
        # فیلتر بر اساس بیمار
        patient_id = self.request.query_params.get('patient', None)
        if patient_id:
            queryset = queryset.filter(prescription__patient__file_number=patient_id)
        
        # فیلتر بر اساس تاریخ
        date = self.request.query_params.get('date', None)
        if date:
            queryset = queryset.filter(distribution_date=date)
        
        return queryset

    def perform_create(self, serializer):
        # محاسبه مقدار باقی‌مانده
        prescription = serializer.validated_data['prescription']
        amount = serializer.validated_data['amount']
        
        total_distributed = MedicationDistribution.objects.filter(
            prescription=prescription
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        remaining = prescription.total_prescribed - (total_distributed + amount)
        
        if remaining < 0:
            raise serializers.ValidationError(
                "مقدار توزیع شده بیشتر از مقدار تجویز شده است."
            )
        
        serializer.save(remaining=remaining)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = Payment.objects.all()
        
        # فیلتر بر اساس بیمار
        patient_id = self.request.query_params.get('patient', None)
        if patient_id:
            queryset = queryset.filter(patient__file_number=patient_id)
        
        # فیلتر بر اساس نوع پرداخت
        payment_type = self.request.query_params.get('payment_type', None)
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        
        # فیلتر بر اساس تاریخ
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        
        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """گزارش خلاصه پرداخت‌ها"""
        # پارامترهای فیلتر
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        period = request.query_params.get('period', 'daily')  # daily, weekly, monthly
        patient_id = request.query_params.get('patient', None)
        
        # پایه کوئری
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        if patient_id:
            queryset = queryset.filter(patient__file_number=patient_id)
        
        # تجمیع بر اساس دوره
        if period == 'daily':
            payments = queryset.values('payment_date').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('payment_date')
        elif period == 'weekly':
            payments = queryset.extra(select={'week': "EXTRACT(week FROM payment_date)"}).values(
                'week'
            ).annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('week')
        else:  # monthly
            payments = queryset.extra(select={'month': "EXTRACT(month FROM payment_date)"}).values(
                'month'
            ).annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('month')
        
        # تجمیع بر اساس نوع پرداخت
        payment_types = queryset.values('payment_type').annotate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        return Response({
            'summary_by_period': payments,
            'summary_by_type': payment_types,
            'total_amount': queryset.aggregate(total=Sum('amount'))['total'],
            'total_count': queryset.count()
        })
