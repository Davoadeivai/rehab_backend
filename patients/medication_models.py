from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_jalali.db import models as jmodels
from .patient_model import Patient


class Medication(models.Model):
    name = models.CharField("نام دارو", max_length=100, unique=True)
    unit = models.CharField("واحد", max_length=50, help_text="مثال: قرص، میلی‌لیتر، گرم")

    def __str__(self):
        return f"{self.name} ({self.unit})"

    class Meta:
        verbose_name = "دارو"
        verbose_name_plural = "داروها"

class PatientMedication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, verbose_name="دارو")
    initial_quantity = models.DecimalField("مقدار اولیه", max_digits=10, decimal_places=2)
    current_quantity = models.DecimalField("مقدار فعلی", max_digits=10, decimal_places=2)
    assigned_date = models.DateTimeField("تاریخ تخصیص", default=timezone.now)

    def __str__(self):
        return f"{self.patient} - {self.medication.name}: {self.current_quantity}/{self.initial_quantity}"

    class Meta:
        verbose_name = "داروی بیمار"
        verbose_name_plural = "داروهای بیماران"
        unique_together = ('patient', 'medication')

class DispensingRecord(models.Model):
    patient_medication = models.ForeignKey(PatientMedication, on_delete=models.CASCADE, verbose_name="داروی تخصیص یافته به بیمار")
    dispensed_quantity = models.DecimalField("مقدار توزیع شده", max_digits=10, decimal_places=2)
    dispensing_date = models.DateTimeField("تاریخ توزیع", default=timezone.now)
    # dispensed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="توزیع کننده") # Assuming User model exists

    def __str__(self):
        return f"{self.patient_medication.patient} - {self.dispensed_quantity} {self.patient_medication.medication.unit} {self.patient_medication.medication.name} در {self.dispensing_date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "رکورد توزیع دارو"
        verbose_name_plural = "رکوردهای توزیع دارو"
        ordering = ['-dispensing_date']

class Service(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('drug', 'دارو'),
        ('visit', 'ویزیت'),
        ('lab', 'آزمایش'),
        ('other', 'سایر'),
    ]
    name = models.CharField("نام خدمت", max_length=100)
    service_type = models.CharField("نوع خدمت", max_length=20, choices=SERVICE_TYPE_CHOICES)
    unit_price = models.DecimalField("قیمت واحد", max_digits=10, decimal_places=2)
    description = models.TextField("توضیحات", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"

    class Meta:
        verbose_name = "خدمت"
        verbose_name_plural = "خدمات"


class ServiceTransaction(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="خدمت")
    date = models.DateTimeField("تاریخ خدمت", default=timezone.now)
    quantity = models.DecimalField("تعداد/مقدار", max_digits=10, decimal_places=2, default=1)
    total_cost = models.DecimalField("هزینه کل", max_digits=10, decimal_places=2, blank=True)
    notes = models.TextField("توضیحات", blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.service.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"تراکنش {self.id}: {self.patient} - {self.service.name}"

    class Meta:
        verbose_name = "تراکنش خدمت"
        verbose_name_plural = "تراکنش‌های خدمات"
        ordering = ['-date']


class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('pos', 'کارتخوان (POS)'),
        ('cash', 'نقد'),
        ('online', 'آنلاین (درگاه پرداخت)'),
        ('transfer', 'کارت به کارت'),
        ('other', 'سایر'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    prescription = models.ForeignKey('Prescription', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="نسخه مرتبط")
    payment_type = models.CharField("نوع پرداخت", max_length=20, choices=PAYMENT_TYPE_CHOICES, default='pos')
    amount = models.DecimalField("مبلغ", max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField("تاریخ پرداخت", default=timezone.now)
    description = models.TextField("توضیحات", blank=True, null=True)
    transactions = models.ManyToManyField('ServiceTransaction', blank=True, verbose_name="تراکنش‌های مرتبط")

    def __str__(self):
        return f"پرداخت {self.id}: {self.patient} - {self.amount} در {self.payment_date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
        ordering = ['-payment_date']

class MedicationType(models.Model):
    name = models.CharField("نام دارو", max_length=100)
    description = models.TextField("توضیحات", blank=True, null=True)
    unit = models.CharField("واحد", max_length=50, help_text="مثال: میلی‌گرم، قرص")
    default_dose = models.DecimalField("دوز پیش‌فرض", max_digits=10, decimal_places=2, null=True, blank=True, help_text="دوز پیشنهادی برای نمایش در فرم نسخه")
    
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

    def save(self, *args, **kwargs):
        # Date consistency check
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("تاریخ شروع باید قبل از تاریخ پایان باشد.")

        # total_prescribed validation
        if self.daily_dose is not None and self.treatment_duration is not None:
            expected_total_prescribed = self.daily_dose * self.treatment_duration
            if self.total_prescribed != expected_total_prescribed:
                raise ValidationError(
                    f"مقدار کل تجویز شده ({self.total_prescribed}) با مقدار محاسبه شده ({expected_total_prescribed}) مغایرت دارد."
                )
        elif self.total_prescribed is not None:
            # This case implies one of daily_dose or treatment_duration is None,
            # but total_prescribed is set, which is likely an error.
            # However, the fields daily_dose and treatment_duration are non-nullable by model definition.
            # This check is more of a safeguard for unexpected NoneType errors if data integrity is somehow bypassed.
            raise ValidationError("دوز روزانه و مدت درمان برای محاسبه مقدار کل تجویز شده الزامی است.")

        super().save(*args, **kwargs)
    
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
        
    def save(self, *args, **kwargs):
        prescription = self.prescription

        # Distribution Date within Prescription Period validation
        if self.distribution_date and prescription.start_date and self.distribution_date < prescription.start_date:
            raise ValidationError("تاریخ توزیع نمی‌تواند قبل از تاریخ شروع نسخه باشد.")

        if self.distribution_date and prescription.end_date and self.distribution_date > prescription.end_date:
            raise ValidationError("تاریخ توزیع نمی‌تواند بعد از تاریخ پایان نسخه باشد.")

        # Amount vs. Total Prescribed validation (cumulative)
        distributed_so_far = MedicationDistribution.objects.filter(prescription=prescription)
        if self.pk:  # if updating, exclude current instance from sum
            distributed_so_far = distributed_so_far.exclude(pk=self.pk)

        total_previously_distributed = sum(dist.amount for dist in distributed_so_far)

        if (total_previously_distributed + self.amount) > prescription.total_prescribed:
            raise ValidationError(
                f"مقدار توزیع شده ({total_previously_distributed + self.amount}) "
                f"بیشتر از مقدار کل تجویز شده ({prescription.total_prescribed}) است."
            )

        # Inventory management logic
        is_new_distribution = not self.pk

        if is_new_distribution:
            try:
                inventory = prescription.medication_type.inventory
                if inventory.current_stock >= self.amount:
                    inventory.current_stock -= self.amount
                else:
                    raise ValidationError("موجودی کافی برای این دارو در انبار نیست.")
            except DrugInventory.DoesNotExist:
                raise ValidationError("موجودی برای این دارو تعریف نشده است.")
            except AttributeError:
                raise ValidationError("ساختار اطلاعاتی دارو یا انبار دارو صحیح نیست.")

        # --- کسر سهمیه بیمار ---
        if is_new_distribution:
            # کم کردن از سهمیه بیمار
            try:
                quota = DrugQuota.objects.get(patient=prescription.patient)
                if quota.remaining_quota >= float(self.amount):
                    quota.remaining_quota -= float(self.amount)
                    quota.save()
                else:
                    raise ValidationError("سهمیه باقی‌مانده بیمار برای این مقدار کافی نیست.")
            except DrugQuota.DoesNotExist:
                raise ValidationError("سهمیه‌ای برای این بیمار تعریف نشده است.")

        super().save(*args, **kwargs)

        if is_new_distribution:
            try:
                inventory = prescription.medication_type.inventory
                inventory.save()
            except DrugInventory.DoesNotExist:
                raise ValidationError("موجودی برای این دارو تعریف نشده است (هنگام ذخیره نهایی انبار).")
            except AttributeError:
                raise ValidationError("ساختار اطلاعاتی دارو یا انبار دارو صحیح نیست (هنگام ذخیره نهایی انبار).")

    def delete(self, *args, **kwargs):
        # بازگرداندن به موجودی داروخانه
        try:
            inventory = self.prescription.medication_type.inventory
            inventory.current_stock += self.amount
            inventory.save()
        except DrugInventory.DoesNotExist:
            pass
        # بازگرداندن به سهمیه بیمار
        try:
            quota = DrugQuota.objects.get(patient=self.prescription.patient)
            quota.remaining_quota += float(self.amount)
            quota.save()
        except DrugQuota.DoesNotExist:
            pass
        super().delete(*args, **kwargs)

class DrugInventory(models.Model):
    medication_type = models.OneToOneField(
        MedicationType, 
        on_delete=models.CASCADE,
        verbose_name="نوع دارو",
        related_name='inventory'
    )
    current_stock = models.DecimalField(
        "موجودی فعلی", 
        max_digits=10, 
        decimal_places=2,
        default=0
    )
    minimum_stock = models.DecimalField(
        "حداقل موجودی", 
        max_digits=10, 
        decimal_places=2,
        default=10,
        help_text="هشدار زمانی که موجودی به این مقدار برسد"
    )
    last_updated = jmodels.jDateTimeField(
        "آخرین به‌روزرسانی",
        auto_now=True
    )

    def __str__(self):
        return f"{self.medication_type.name} - موجودی: {self.current_stock} {self.medication_type.unit}"

    class Meta:
        verbose_name = "موجودی دارو"
        verbose_name_plural = "موجودی داروها"

class DrugQuota(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    total_quota = models.FloatField()  # کل سهمیه
    remaining_quota = models.FloatField()  # سهمیه باقی‌مانده

class DrugAppointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.FloatField()  # مقدار دارو برای این نوبت
    is_paid = models.BooleanField(default=False)

class DrugReceipt(models.Model):
    appointment = models.ForeignKey(DrugAppointment, on_delete=models.CASCADE)
    received_at = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    payment = models.FloatField()


class MedicationAdministration(models.Model):
    DOSE_CHOICES = [
        ("5mg", "۵mg"),
        ("20mg", "۲۰mg"),
        ("40mg", "۴۰mg"),
        ("82mg", "۸۲mg"),
        ("82/8", "۸۲/۸"),
        ("0.4", "۰/۴"),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, verbose_name="دارو")
    administration_date = jmodels.jDateField("تاریخ تجویز")
    dose = models.CharField("دوز مصرفی", max_length=10, choices=DOSE_CHOICES, null=True, blank=True)
    administered_quantity = models.DecimalField("مقدار تجویز شده", max_digits=10, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField("هزینه دریافتی (تومان)", max_digits=10, decimal_places=2, null=True, blank=True)
    signature = models.CharField("امضاء دریافت‌کننده", max_length=100, blank=True, null=True)
    notes = models.TextField("یادداشت‌ها", blank=True, null=True)

    def __str__(self):
        return f"{self.patient} - {self.medication.name} on {self.administration_date}"

    class Meta:
        verbose_name = "تجویز دارو"
        verbose_name_plural = "تجویز داروها"
        ordering = ['-administration_date']
