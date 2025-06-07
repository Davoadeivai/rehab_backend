from django.db import models
from django_jalali.db import models as jmodels
from django.utils import timezone
from patients.models import Patient

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'رزرو شده'),
        ('completed', 'تکمیل شده'),
        ('cancelled', 'لغو شده'),
        ('no_show', 'عدم حضور'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    appointment_date = jmodels.jDateTimeField("تاریخ و زمان نوبت")
    status = models.CharField("وضعیت", max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField("یادداشت‌ها", blank=True, null=True)
    created_at = models.DateTimeField("تاریخ ایجاد", default=timezone.now)
    updated_at = models.DateTimeField("تاریخ به‌روزرسانی", default=timezone.now)

    def __str__(self):
        return f"{self.patient} - {self.appointment_date}"

    class Meta:
        verbose_name = "نوبت"
        verbose_name_plural = "نوبت‌ها"
        ordering = ['-appointment_date'] 