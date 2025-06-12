from django.db import models
from django_jalali.db import models as jmodels
from .patient_model import Patient
from .medication_models import Payment


class Notification(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField("عنوان", max_length=255)
    message = models.TextField("پیام")
    is_read = models.BooleanField("خوانده شده", default=False)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان‌ها"
        ordering = ['-created_at']

class PatientFile(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    file = models.FileField("فایل", upload_to='patient_files/')
    description = models.TextField("توضیحات", blank=True, null=True)
    uploaded_at = models.DateTimeField("تاریخ بارگذاری", auto_now_add=True)

    def __str__(self):
        return f"فایل {self.description} برای {self.patient}"

    class Meta:
        verbose_name = "فایل بیمار"
        verbose_name_plural = "فایل‌های بیماران"

class TreatmentPlan(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    start_date = jmodels.jDateField("تاریخ شروع")
    end_date = jmodels.jDateField("تاریخ پایان", null=True, blank=True)
    description = models.TextField("توضیحات")
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ به‌روزرسانی", auto_now_add=True)

    def __str__(self):
        return f"برنامه درمانی {self.patient} از {self.start_date}"

    class Meta:
        verbose_name = "برنامه درمانی"
        verbose_name_plural = "برنامه‌های درمانی"

class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    visit_date = jmodels.jDateTimeField("تاریخ و زمان ویزیت")
    description = models.TextField("توضیحات ویزیت", blank=True, null=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ به‌روزرسانی", auto_now_add=True)

    def __str__(self):
        return f"ویزیت {self.patient} در {self.visit_date}"

    class Meta:
        verbose_name = "ویزیت"
        verbose_name_plural = "ویزیت‌ها"
        ordering = ['-visit_date']

class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    condition = models.CharField("وضعیت پزشکی", max_length=255)
    diagnosis_date = jmodels.jDateField("تاریخ تشخیص", null=True, blank=True)
    notes = models.TextField("یادداشت‌ها", blank=True, null=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("تاریخ به‌روزرسانی", auto_now_add=True)

    def __str__(self):
        return f"سابقه پزشکی {self.patient}: {self.condition}"

    class Meta:
        verbose_name = "سابقه پزشکی"
        verbose_name_plural = "سوابق پزشکی"








        



class Contact(models.Model):
    """مدل تماس با ما"""
    name = models.CharField(max_length=100, verbose_name='نام')
    email = models.EmailField(verbose_name='ایمیل')
    subject = models.CharField(max_length=200, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')

    class Meta:
        verbose_name = 'تماس'
        verbose_name_plural = 'تماس‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Support(models.Model):
    """مدل پشتیبانی فنی"""
    PRIORITY_CHOICES = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'زیاد'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیحات')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='اولویت')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    is_resolved = models.BooleanField(default=False, verbose_name='حل شده')

    class Meta:
        verbose_name = 'پشتیبانی'
        verbose_name_plural = 'پشتیبانی‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Feedback(models.Model):
    """مدل پیشنهادات و انتقادات"""
    TYPE_CHOICES = [
        ('suggestion', 'پیشنهاد'),
        ('complaint', 'انتقاد'),
        ('praise', 'تعریف و تمجید'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(verbose_name='توضیحات')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='suggestion', verbose_name='نوع')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')

    class Meta:
        verbose_name = 'پیشنهاد'
        verbose_name_plural = 'پیشنهادات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title






