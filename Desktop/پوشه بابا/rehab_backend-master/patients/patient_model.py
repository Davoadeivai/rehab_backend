import hashlib
import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_jalali.db import models as jmodels
from django.db.models import Max
from django.utils.crypto import get_random_string

class Patient(models.Model):
    GENDER_CHOICES = [
        ('male', 'مرد'),
        ('female', 'زن'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'مجرد'),
        ('married', 'متأهل'),
        ('divorced', 'مطلقه'),
        ('widowed', 'همسر فوت شده'),
    ]
    
    EDUCATION_CHOICES = [
        ('illiterate', 'بی‌سواد'),
        ('elementary', 'ابتدایی'),
        ('middle_school', 'راهنمایی'),
        ('high_school', 'دبیرستان'),
        ('diploma', 'دیپلم'),
        ('associate', 'فوق دیپلم'),
        ('bachelor', 'لیسانس'),
        ('master', 'فوق لیسانس'),
        ('phd', 'دکترا'),
    ]
    
    DRUG_TYPE_CHOICES = [
        ('opium', 'تریاک'),
        ('heroin', 'هروئین'),
        ('meth', 'شیشه'),
        ('other', 'سایر'),
    ]
    
    TREATMENT_TYPE_CHOICES = [
        ('maintenance', 'نگهدارنده'),
        ('detox', 'سم‌زدایی'),
        ('other', 'سایر'),
    ]

    file_number = models.CharField(
        "شماره پرونده",
        max_length=20,
        unique=True,
        primary_key=True,
        blank=True,
        help_text="شماره پرونده به صورت خودکار تولید می‌شود"
    )
    first_name = models.CharField("نام", max_length=50)
    last_name = models.CharField("نام خانوادگی", max_length=50)
    national_code = models.CharField("کد ملی", max_length=10, unique=True)
    patient_code = models.CharField(
        "کد بیمار",
        max_length=6,
        unique=True,
        blank=True,
        null=True,
        help_text="به صورت خودکار از کد ملی تولید می‌شود"
    )
    date_birth = jmodels.jDateField("تاریخ تولد", null=True, blank=True, help_text="مثال: 1402/01/01")
    gender = models.CharField("جنسیت", max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    phone_number = models.CharField("شماره تلفن", max_length=15, null=True, blank=True)
    address = models.TextField("آدرس", null=True, blank=True)
    marital_status = models.CharField("وضعیت تأهل", max_length=50, choices=MARITAL_STATUS_CHOICES)
    education = models.CharField("تحصیلات", max_length=100, default="Unknown", choices=EDUCATION_CHOICES)
    drug_type = models.CharField("نوع ماده مصرفی", max_length=100, null=True, blank=True, choices=DRUG_TYPE_CHOICES)
    treatment_type = models.CharField("نوع درمان", max_length=100, choices=TREATMENT_TYPE_CHOICES)
    usage_duration = models.CharField("مدت مصرف", max_length=50)
    admission_date = jmodels.jDateField("تاریخ پذیرش", null=True, blank=True, help_text="مثال: ۱۴۰۲/۰۱/۰۱")
    treatment_withdrawal_date = jmodels.jDateField("تاریخ خروج از درمان", null=True, blank=True, help_text="مثال: ۱۴۰۲/۰۱/۰۱")
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ به‌روزرسانی", auto_now=True)
    is_active = models.BooleanField("سن", default=True)
    

    def generate_file_number(self):
        """
        Generate a sophisticated file number using:
        - Year (2 digits)
        - Month (2 digits)
        - Day (2 digits)
        - First 3 letters of last name (Persian)
        - First 3 letters of first name (Persian)
        - Last 4 digits of national code
        - Random 3-digit checksum
        """
        now = timezone.now()
        
        # Get first 3 letters of first and last name (Persian)
        first_name_part = self.first_name[:3] if self.first_name else 'NNN'
        last_name_part = self.last_name[:3] if self.last_name else 'NNN'
        
        # Get last 4 digits of national code
        national_code_part = self.national_code[-4:] if self.national_code and len(self.national_code) >= 4 else '0000'
        
        # Generate a random 3-digit checksum
        checksum = get_random_string(3, '123456789')
        
        # Format: YYMMDD-LAST3-FIRST3-NAT4-CHK3
        file_number = (
            f"{now.strftime('%y%m%d')}-{last_name_part}-{first_name_part}-{national_code_part}-{checksum}"
        )
        
        return file_number.upper()

    def save(self, *args, **kwargs):
        # National code validation
        if self.national_code:
            if not self.national_code.isdigit():
                raise ValidationError("کد ملی باید فقط شامل اعداد باشد.")
            if len(self.national_code) != 10:
                raise ValidationError("کد ملی باید دقیقا ۱۰ رقم باشد.")

        # Phone number validation
        if self.phone_number:
            if not self.phone_number.isdigit():
                raise ValidationError("شماره تلفن باید فقط شامل اعداد باشد.")
            if len(self.phone_number) != 11:
                raise ValidationError("شماره تلفن باید ۱۱ رقم باشد.")

        # Date consistency checks
        if self.date_birth and self.admission_date:
            if self.date_birth >= self.admission_date:
                raise ValidationError("تاریخ تولد باید قبل از تاریخ پذیرش باشد.")

        if self.admission_date and self.treatment_withdrawal_date:
            if self.admission_date >= self.treatment_withdrawal_date:
                raise ValidationError("تاریخ پذیرش باید قبل از تاریخ خروج از درمان باشد.")

        if not self.pk:
            self.created_at = timezone.now()
            # Generate patient code from national code if not set
            if not self.patient_code and self.national_code:
                self.patient_code = self.national_code[-6:]
            
            # Generate file number if not set
            if not self.file_number:
                self.file_number = self.generate_file_number()
                
                # Ensure uniqueness
                while Patient.objects.filter(file_number=self.file_number).exists():
                    self.file_number = self.generate_file_number()
                    
        self.updated_at = timezone.now()
        
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - پرونده: {self.file_number}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "بیمار"
        verbose_name_plural = "بیماران"
