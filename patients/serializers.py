from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from .models import Patient
from .medication_models import MedicationType, Prescription, MedicationDistribution, Payment
from .utils import format_jalali_date, format_jalali_full_date
import jdatetime
from django.utils import timezone


# ----------------------------
# Register Serializer
# ----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate_username(self, value):
        import re
        if not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=\[\]{}|;:,.<>?~`-]+$', value):
            raise serializers.ValidationError('نام کاربری فقط می‌تواند شامل حروف انگلیسی، اعداد و کاراکترهای بالای کیبورد باشد.')
        if len(value) < 4 or len(value) > 30:
            raise serializers.ValidationError('نام کاربری باید بین ۴ تا ۳۰ کاراکتر باشد.')
        return value

    def validate_first_name(self, value):
        import re
        if value and not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=\[\]{}|;:,.<>?~`-]+$', value):
            raise serializers.ValidationError('نام فقط می‌تواند شامل حروف انگلیسی، اعداد و کاراکترهای بالای کیبورد باشد.')
        if value and len(value) > 30:
            raise serializers.ValidationError('نام نباید بیش از ۳۰ کاراکتر باشد.')
        return value

    def validate_last_name(self, value):
        import re
        if value and not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=\[\]{}|;:,.<>?~`-]+$', value):
            raise serializers.ValidationError('نام خانوادگی فقط می‌تواند شامل حروف انگلیسی، اعداد و کاراکترهای بالای کیبورد باشد.')
        if value and len(value) > 30:
            raise serializers.ValidationError('نام خانوادگی نباید بیش از ۳۰ کاراکتر باشد.')
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("رمز عبور و تکرار آن یکسان نیستند.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # حذف فیلد تکراری
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# ----------------------------
# Login Serializer
# ----------------------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("نام کاربری یا رمز عبور اشتباه است.")
        return data


# ----------------------------
# Patient Serializer
# ----------------------------
class PatientSerializer(serializers.ModelSerializer):
    date_birth = serializers.CharField(required=False, allow_blank=True, label="تاریخ تولد")
    admission_date = serializers.CharField(required=False, allow_blank=True, label="تاریخ پذیرش")
    treatment_withdrawal_date = serializers.CharField(required=False, allow_blank=True, label="تاریخ خروج از درمان")
    gender_display = serializers.SerializerMethodField()
    formatted_dates = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'file_number', 'first_name', 'last_name', 'national_code',
            'date_birth', 'gender', 'gender_display', 'phone_number',
            'address', 'marital_status', 'education', 'drug_type',
            'treatment_type', 'usage_duration', 'admission_date',
            'treatment_withdrawal_date', 'formatted_dates'
        ]
        labels = {
            'file_number': 'شماره پرونده',
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'national_code': 'کد ملی',
            'date_birth': 'تاریخ تولد',
            'gender': 'جنسیت',
            'phone_number': 'شماره تلفن',
            'address': 'آدرس',
            'marital_status': 'وضعیت تأهل',
            'education': 'تحصیلات',
            'drug_type': 'نوع ماده مصرفی',
            'treatment_type': 'نوع درمان',
            'usage_duration': 'مدت مصرف',
            'admission_date': 'تاریخ پذیرش',
            'treatment_withdrawal_date': 'تاریخ خروج از درمان'
        }

    def get_gender_display(self, obj):
        return obj.get_gender_display() if obj.gender else ''

    def get_formatted_dates(self, obj):
        return {
            'date_birth': format_jalali_full_date(obj.date_birth),
            'admission_date': format_jalali_full_date(obj.admission_date),
            'treatment_withdrawal_date': format_jalali_full_date(obj.treatment_withdrawal_date)
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # تبدیل تاریخ‌های میلادی به شمسی با فرمت فارسی
        date_fields = ['date_birth', 'admission_date', 'treatment_withdrawal_date']
        for field in date_fields:
            if getattr(instance, field):
                jalali_date = getattr(instance, field)
                data[field] = format_jalali_date(jalali_date)
            else:
                data[field] = ""
        return data

    def to_internal_value(self, data):
        date_fields = ['date_birth', 'admission_date', 'treatment_withdrawal_date']
        data_copy = data.copy()

        for field in date_fields:
            if field in data_copy and data_copy[field]:
                try:
                    if isinstance(data_copy[field], str):
                        # پاک کردن کاراکترهای اضافی
                        date_str = data_copy[field].strip().replace('-', '/').replace('_', '/')
                        parts = date_str.split('/')
                        if len(parts) == 3:
                            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                            # تبدیل به تاریخ جلالی
                            jdate = jdatetime.date(year, month, day)
                            data_copy[field] = jdate
                except ValueError as e:
                    raise serializers.ValidationError({
                        field: "لطفاً تاریخ را به فرمت صحیح وارد کنید (مثال: ۱۴۰۲/۰۱/۰۱)"
                    })

        return super().to_internal_value(data_copy)


# ----------------------------
# Family Serializer
# ----------------------------
# class FamilySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Family
#         fields = '__all__'


# # ----------------------------
# # Medication Serializer
# # ----------------------------
# class MedicationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Medication
#         fields = '__all__'


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("کاربری با این ایمیل یافت نشد.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    token = serializers.CharField()
    uidb64 = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("رمز عبور و تکرار آن یکسان نیستند.")
        return data

    def validate_password(self, value):
        import re
        if not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=\[\]{}|;:,.<>?~`-]+$', value):
            raise serializers.ValidationError('رمز عبور فقط می‌تواند شامل حروف انگلیسی، اعداد و کاراکترهای بالای کیبورد باشد.')
        if len(value) < 8 or len(value) > 30:
            raise serializers.ValidationError('رمز عبور باید بین ۸ تا ۳۰ کاراکتر باشد.')
        return value

class MedicationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicationType
        fields = ['id', 'name', 'description', 'unit']
        labels = {
            'name': 'نام دارو',
            'description': 'توضیحات',
            'unit': 'واحد'
        }

class PrescriptionSerializer(serializers.ModelSerializer):
    medication_type_name = serializers.CharField(source='medication_type.name', read_only=True)
    patient_name = serializers.CharField(source='patient.__str__', read_only=True)
    formatted_dates = serializers.SerializerMethodField()
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'patient', 'patient_name', 'medication_type', 'medication_type_name',
            'daily_dose', 'treatment_duration', 'start_date', 'end_date',
            'total_prescribed', 'notes', 'created_at', 'formatted_dates'
        ]
        labels = {
            'patient': 'بیمار',
            'medication_type': 'نوع دارو',
            'daily_dose': 'دوز روزانه',
            'treatment_duration': 'مدت درمان (روز)',
            'start_date': 'تاریخ شروع',
            'end_date': 'تاریخ پایان',
            'total_prescribed': 'مقدار کل تجویز شده',
            'notes': 'یادداشت‌ها',
            'created_at': 'تاریخ ایجاد'
        }

    def get_formatted_dates(self, obj):
        return {
            'start_date': format_jalali_full_date(obj.start_date),
            'end_date': format_jalali_full_date(obj.end_date),
            'created_at': format_jalali_date(obj.created_at, include_time=True)
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # تبدیل تاریخ‌ها به فرمت شمسی
        date_fields = ['start_date', 'end_date', 'created_at']
        for field in date_fields:
            if data[field]:
                if field == 'created_at':
                    data[field] = format_jalali_date(getattr(instance, field), include_time=True)
                else:
                    data[field] = format_jalali_date(getattr(instance, field))
        return data

class MedicationDistributionSerializer(serializers.ModelSerializer):
    prescription_details = PrescriptionSerializer(source='prescription', read_only=True)
    formatted_dates = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicationDistribution
        fields = [
            'id', 'prescription', 'prescription_details', 'distribution_date',
            'amount', 'remaining', 'notes', 'created_at', 'formatted_dates'
        ]
        labels = {
            'prescription': 'نسخه',
            'distribution_date': 'تاریخ توزیع',
            'amount': 'مقدار',
            'remaining': 'باقی‌مانده',
            'notes': 'یادداشت‌ها',
            'created_at': 'تاریخ ایجاد'
        }

    def get_formatted_dates(self, obj):
        return {
            'distribution_date': format_jalali_full_date(obj.distribution_date),
            'created_at': format_jalali_date(obj.created_at, include_time=True)
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # تبدیل تاریخ‌ها به فرمت شمسی
        date_fields = ['distribution_date', 'created_at']
        for field in date_fields:
            if data[field]:
                if field == 'created_at':
                    data[field] = format_jalali_date(getattr(instance, field), include_time=True)
                else:
                    data[field] = format_jalali_date(getattr(instance, field))
        return data

class PaymentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.__str__', read_only=True)
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    formatted_dates = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'patient', 'patient_name', 'payment_date', 'amount',
            'payment_type', 'payment_type_display', 'description', 'created_at',
            'formatted_dates'
        ]
        labels = {
            'patient': 'بیمار',
            'payment_date': 'تاریخ پرداخت',
            'amount': 'مبلغ',
            'payment_type': 'نوع پرداخت',
            'description': 'توضیحات',
            'created_at': 'تاریخ ایجاد'
        }

    def get_formatted_dates(self, obj):
        return {
            'payment_date': format_jalali_full_date(obj.payment_date),
            'created_at': format_jalali_date(obj.created_at, include_time=True)
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # تبدیل تاریخ‌ها به فرمت شمسی
        date_fields = ['payment_date', 'created_at']
        for field in date_fields:
            if data[field]:
                if field == 'created_at':
                    data[field] = format_jalali_date(getattr(instance, field), include_time=True)
                else:
                    data[field] = format_jalali_date(getattr(instance, field))
        
        # Format amount with commas for better readability
        if data['amount']:
            data['amount_display'] = "{:,}".format(data['amount'])
        
        return data
