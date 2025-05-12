from django.db import models
from django.utils.translation import gettext_lazy as _

class Patient(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'نقدی', _('نقدی')
        CARD = 'کارت', _('کارت')
        OTHER = 'سایر', _('سایر')

    # فیلدهای اصلی
    full_name = models.CharField(_('نام کامل'), max_length=100)
    file_number = models.CharField(_('شماره پرونده'), max_length=20, unique=True)
    system_code = models.CharField(_('کد سامانه'), max_length=20)
    drug_type = models.CharField(_('نوع دارو'), max_length=100)
    treatment_period = models.CharField(_('دوره دارویی'), max_length=50)
    th = models.DecimalField(_('T.H.'), max_digits=4, decimal_places=1)
    payment_amount = models.DecimalField(_('هزینه دریافتی'), max_digits=12, decimal_places=2)
    payment_method = models.CharField(_('نوع پرداخت'), max_length=20, choices=PaymentMethod.choices)
    signature = models.BooleanField(_('امضا'), default=False)
    admission_date = models.DateField(_('تاریخ پذیرش'), auto_now_add=True)

    class Meta:
        db_table = 'بیماران'

    def __str__(self):
        return f"{self.full_name} - {self.file_number}"

class Family(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='شماره_پرونده')
    members_count = models.IntegerField(_('تعداد اعضا'))
    support_type = models.CharField(_('نوع حمایت'), max_length=50)
    recorded_deviations = models.TextField(_('انحرافات ثبت شده'))

    class Meta:
        db_table = 'خانواده'

class Medication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='شماره_پرونده')
    dosage_40mg = models.IntegerField(_('دوز ۴۰mg'))
    dosage_20mg = models.IntegerField(_('دوز ۲۰mg'))
    dosage_5mg = models.IntegerField(_('دوز ۵mg'))

    class Meta:
        db_table = 'داروها'

