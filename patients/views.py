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
from django.db.models import Count, Sum, Q
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, timedelta
import jdatetime
from .utils import format_jalali_date, format_jalali_full_date, format_number
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from rest_framework import generics
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import PatientForm

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
import xlwt
import io

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
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="patients.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Patients')

    # Sheet header
    row_num = 0
    columns = ['نام', 'نام خانوادگی', 'کد ملی', 'شماره پرونده', 'تاریخ پذیرش']
    
    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title)

    # Sheet body
    rows = Patient.objects.values_list('first_name', 'last_name', 'national_code', 'file_number', 'admission_date')
    for row in rows:
        row_num += 1
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, str(cell_value))

    wb.save(response)
    return response

@login_required
def export_to_pdf(request):
    template_path = 'patients/patient_list_pdf.html'
    context = {'patients': Patient.objects.all()}
    
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="patients.pdf"'
    
    # Find the template and render it
    template = get_template(template_path)
    html = template.render(context)
    
    # Create a PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # If error then show some funny view
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

# Template Views
@login_required
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/patient_list.html', {'patients': patients})

@login_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, 'بیمار با موفقیت ثبت شد.')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientForm()
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'ثبت بیمار جدید'})

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'patients/patient_detail.html', {'patient': patient})

@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save()
            messages.success(request, 'اطلاعات بیمار با موفقیت به‌روزرسانی شد.')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'ویرایش اطلاعات بیمار'})

@login_required
def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'بیمار با موفقیت حذف شد.')
        return redirect('patients:patient_list')
    return render(request, 'patients/patient_confirm_delete.html', {'patient': patient})

# API Views
class PatientListCreateAPIView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class PatientRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

@login_required
def prescription_create(request):
    patient_id = request.GET.get('patient')
    if request.method == 'POST':
        # TODO: Add prescription creation logic
        messages.success(request, 'نسخه با موفقیت ثبت شد.')
        return redirect('patients:patient_detail', pk=patient_id)
    return render(request, 'patients/prescription_form.html', {
        'patient_id': patient_id,
        'title': 'ثبت نسخه جدید'
    })

@login_required
def payment_create(request):
    patient_id = request.GET.get('patient')
    if request.method == 'POST':
        # TODO: Add payment creation logic
        messages.success(request, 'پرداخت با موفقیت ثبت شد.')
        return redirect('patients:patient_detail', pk=patient_id)
    return render(request, 'patients/payment_form.html', {
        'patient_id': patient_id,
        'title': 'ثبت پرداخت جدید'
    })

@login_required
def prescription_list(request):
    prescriptions = Prescription.objects.all().order_by('-created_at')
    return render(request, 'patients/prescription_list.html', {'prescriptions': prescriptions})

@login_required
def distribution_list(request):
    distributions = MedicationDistribution.objects.all().order_by('-distribution_date')
    return render(request, 'patients/distribution_list.html', {'distributions': distributions})

@login_required
def distribution_create(request):
    if request.method == 'POST':
        # TODO: Add distribution creation logic
        messages.success(request, 'توزیع دارو با موفقیت ثبت شد.')
        return redirect('patients:distribution_list')
    return render(request, 'patients/distribution_form.html', {'title': 'ثبت توزیع دارو'})

@login_required
def payment_list(request):
    payments = Payment.objects.all().order_by('-payment_date')
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'patients/payment_list.html', {
        'payments': payments,
        'total_amount': total_amount
    })

@login_required
def report_list(request):
    # آمار کلی
    total_patients = Patient.objects.count()
    active_patients = Patient.objects.filter(treatment_withdrawal_date__isnull=True).count()
    completed_patients = Patient.objects.filter(treatment_withdrawal_date__isnull=False).count()
    
    # آمار پرداخت‌ها
    total_payments = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    payment_by_type = Payment.objects.values('payment_type').annotate(
        total=Sum('amount'),
        count=Count('id')
    )
    
    # آمار توزیع دارو
    total_distributions = MedicationDistribution.objects.count()
    medication_stats = MedicationDistribution.objects.values(
        'prescription__medication_type__name'
    ).annotate(
        total_amount=Sum('amount'),
        count=Count('id')
    )
    
    context = {
        'total_patients': total_patients,
        'active_patients': active_patients,
        'completed_patients': completed_patients,
        'total_payments': total_payments,
        'payment_by_type': payment_by_type,
        'total_distributions': total_distributions,
        'medication_stats': medication_stats,
    }
    
    return render(request, 'patients/report_list.html', context)
