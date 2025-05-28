from django.db import models
from django_jalali.db import models as jmodels
from django.utils import timezone

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

    file_number = models.CharField("شماره پرونده", max_length=20, unique=True, primary_key=True)
    first_name = models.CharField("نام", max_length=50)
    last_name = models.CharField("نام خانوادگی", max_length=50)
    national_code = models.CharField("کد ملی", max_length=10, unique=True)
    date_birth = jmodels.jDateField("تاریخ تولد", null=True, blank=True, help_text="مثال: ۱۴۰۲/۰۱/۰۱")
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
    created_at = models.DateTimeField("تاریخ ایجاد", default=timezone.now)
    updated_at = models.DateTimeField("تاریخ به‌روزرسانی", default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set created_at for new instances
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - پرونده: {self.file_number}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "بیمار"
        verbose_name_plural = "بیماران"

class MedicationType(models.Model):
    name = models.CharField("نام دارو", max_length=100)
    description = models.TextField("توضیحات", blank=True, null=True)
    unit = models.CharField("واحد", max_length=50, help_text="مثال: میلی‌گرم، قرص")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "نوع دارو"
        verbose_name_plural = "انواع دارو"

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    medication_type = models.ForeignKey(MedicationType, on_delete=models.PROTECT, verbose_name="نوع دارو")
    daily_dose = models.DecimalField("دوز روزانه", max_digits=10, decimal_places=2)
    treatment_duration = models.IntegerField("مدت درمان (روز)")
    start_date = jmodels.jDateField("تاریخ شروع")
    end_date = jmodels.jDateField("تاریخ پایان")
    total_prescribed = models.DecimalField("مقدار کل تجویز شده", max_digits=10, decimal_places=2)
    notes = models.TextField("یادداشت‌ها", blank=True, null=True)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient} - {self.medication_type} - از {self.start_date} تا {self.end_date}"
    
    class Meta:
        verbose_name = "نسخه"
        verbose_name_plural = "نسخه‌ها"

class MedicationDistribution(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, verbose_name="نسخه")
    distribution_date = jmodels.jDateField("تاریخ توزیع")
    amount = models.DecimalField("مقدار", max_digits=10, decimal_places=2)
    remaining = models.DecimalField("باقی‌مانده", max_digits=10, decimal_places=2)
    notes = models.TextField("یادداشت‌ها", blank=True, null=True)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    
    def __str__(self):
        return f"{self.prescription.patient} - {self.prescription.medication_type} - {self.distribution_date}"
    
    class Meta:
        verbose_name = "توزیع دارو"
        verbose_name_plural = "توزیع داروها"

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('visit', 'ویزیت'),
        ('medication', 'دارو'),
        ('other', 'سایر'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    payment_date = jmodels.jDateField("تاریخ پرداخت")
    amount = models.DecimalField("مبلغ", max_digits=10, decimal_places=0)
    payment_type = models.CharField("نوع پرداخت", max_length=20, choices=PAYMENT_TYPES)
    description = models.TextField("توضیحات", blank=True, null=True)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient} - {self.amount} ریال - {self.payment_date}"
    
    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"