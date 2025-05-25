from django.db import models
from django_jalali.db import models as jmodels

class Patient(models.Model):
    file_number = models.CharField("شماره پرونده", max_length=20, unique=True, primary_key=True)
    first_name = models.CharField("نام", max_length=50)
    last_name = models.CharField("نام خانوادگی", max_length=50)
    national_code = models.CharField("کد ملی", max_length=10, unique=True)
    # تغییر به تاریخ شمسی
    date_birth = jmodels.jDateField("تاریخ تولد", null=True, blank=True)
    gender = models.CharField("جنسیت", max_length=10, choices=[("male", "مرد"), ("female", "زن")], null=True, blank=True)
    phone_number = models.CharField("شماره تلفن", max_length=15, null=True, blank=True)
    address = models.TextField("آدرس", null=True, blank=True)
    marital_status = models.CharField("وضعیت تأهل", max_length=50)
    education = models.CharField("تحصیلات", max_length=100, default="Unknown")
    drug_type = models.CharField("نوع ماده مصرفی", max_length=100, null=True, blank=True)
    treatment_type = models.CharField("نوع درمان", max_length=100)
    usage_duration = models.CharField("مدت مصرف", max_length=50)
    # تغییر به تاریخ شمسی
    admission_date = jmodels.jDateField("تاریخ پذیرش", null=True, blank=True)
    # تغییر به تاریخ شمسی
    treatment_withdrawal_date = jmodels.jDateField("تاریخ خروج از درمان", null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - پرونده: {self.file_number}"