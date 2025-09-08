from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_jalali.db import models as jmodels
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F
from django.core.validators import MinValueValidator
from .patient_model import Patient

class InventoryLog(models.Model):
    """
    مدل لاگ تغییرات موجودی انبار
    برای ثبت تمام تغییرات در موجودی انبار استفاده می‌شود
    """
    INVENTORY_LOG_TYPES = [
        ('purchase', 'خرید'),
        ('distribution', 'توزیع'),
        ('adjustment', 'تعدیل'),
        ('return', 'عودت'),
        ('waste', 'ضایعات'),
    ]
    
    inventory_item = models.ForeignKey(
        'DrugInventory', 
        on_delete=models.CASCADE,
        verbose_name="آیتم موجودی"
    )
    quantity_change = models.DecimalField(
        "تغییر مقدار",
        max_digits=10,
        decimal_places=2,
        help_text="مقدار مثبت برای افزایش و مقدار منفی برای کاهش موجودی"
    )
    previous_quantity = models.DecimalField(
        "موجودی قبلی",
        max_digits=10,
        decimal_places=2
    )
    new_quantity = models.DecimalField(
        "موجودی جدید",
        max_digits=10,
        decimal_places=2
    )
    log_type = models.CharField(
        "نوع عملیات",
        max_length=20,
        choices=INVENTORY_LOG_TYPES
    )
    reference_type = models.CharField(
        "مرجع عملیات",
        max_length=50,
        help_text="نوع مدل مرجع (مانند 'medicationdistribution')"
    )
    reference_id = models.PositiveIntegerField(
        "شناسه مرجع",
        help_text="شناسه رکورد مرجع"
    )
    notes = models.TextField("توضیحات", blank=True, null=True)
    created_at = jmodels.jDateTimeField("تاریخ ثبت", auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="ثبت کننده",
        related_name='patient_inventory_logs'
    )

    class Meta:
        verbose_name = "لاگ موجودی"
        verbose_name_plural = "لاگ‌های موجودی"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['inventory_item', 'created_at']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]

    def __str__(self):
        return f"{self.get_log_type_display()}: {self.quantity_change} {self.inventory_item.medication_type.unit}"

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
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'تکمیل شده'),
        ('failed', 'ناموفق'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="بیمار")
    prescription = models.ForeignKey('Prescription', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="نسخه مرتبط")
    payment_type = models.CharField("نوع پرداخت", max_length=20, choices=PAYMENT_TYPE_CHOICES, default='pos')
    amount = models.DecimalField("مبلغ", max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField("تاریخ پرداخت", default=timezone.now)
    description = models.TextField("توضیحات", blank=True, null=True)
    transactions = models.ManyToManyField('ServiceTransaction', blank=True, verbose_name="تراکنش‌های مرتبط")
    status = models.CharField("وضعیت پرداخت", max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

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
    """
    مدل توزیع دارو
    برای ثبت هر بار توزیع دارو به بیماران استفاده می‌شود
    """
    prescription = models.ForeignKey(
        Prescription, 
        on_delete=models.PROTECT,  # Changed from CASCADE to PROTECT to preserve history
        verbose_name="نسخه",
        related_name='distributions'
    )
    distribution_date = jmodels.jDateField("تاریخ توزیع")
    amount = models.DecimalField(
        "مقدار",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, "مقدار باید بزرگتر از صفر باشد")]
    )
    remaining = models.DecimalField(
        "باقی‌مانده",
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text="مقدار باقی‌مانده از نسخه پس از این توزیع"
    )
    notes = models.TextField("یادداشت‌ها", blank=True, null=True)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="توزیع کننده",
        related_name='distributions'
    )
    
    class Meta:
        verbose_name = "توزیع دارو"
        verbose_name_plural = "توزیع‌های دارویی"
        ordering = ['-distribution_date', '-created_at']
        indexes = [
            models.Index(fields=['prescription']),
            models.Index(fields=['distribution_date']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"توزیع {self.amount} {self.prescription.medication_type.unit} از {self.prescription}"
    
    def clean(self):
        # Skip validation for existing instances during bulk operations
        if hasattr(self, '_dirty') and self._dirty:
            return
            
        # Validate distribution date is within prescription period
        if hasattr(self, 'prescription'):
            if self.distribution_date < self.prescription.start_date:
                raise ValidationError({
                    'distribution_date': 'تاریخ توزیع نمی‌تواند قبل از تاریخ شروع نسخه باشد'
                })
            if self.distribution_date > self.prescription.end_date:
                raise ValidationError({
                    'distribution_date': 'تاریخ توزیع نمی‌تواند بعد از تاریخ پایان نسخه باشد'
                })
        
        # Validate amount doesn't exceed remaining prescription amount
        if hasattr(self, 'prescription') and hasattr(self, 'amount'):
            total_distributed = MedicationDistribution.objects.filter(
                prescription=self.prescription
            ).exclude(pk=self.pk if self.pk else None).aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            remaining = self.prescription.total_prescribed - total_distributed
            
            if self.amount > remaining:
                raise ValidationError({
                    'amount': f'مقدار توزیع ({self.amount}) نمی‌تواند از مقدار باقی‌مانده نسخه ({remaining}) بیشتر باشد'
                })
    
    def save(self, *args, **kwargs):
        # Calculate remaining before saving
        if self.pk is None:  # New instance
            total_distributed = MedicationDistribution.objects.filter(
                prescription=self.prescription
            ).aggregate(total=Sum('amount'))['total'] or 0
            self.remaining = self.prescription.total_prescribed - (total_distributed + self.amount)
        
        self.full_clean()
        super().save(*args, **kwargs)
        
        # Update prescription status if needed
        if self.remaining <= 0:
            self.prescription.status = 'completed'
            self.prescription.save(update_fields=['status'])
    
    def delete(self, *args, **kwargs):
        # Store the amount before deletion for quota and inventory updates
        amount = self.amount
        prescription = self.prescription
        
        # Delete the record first
        super().delete(*args, **kwargs)
        
        # Update remaining amounts for other distributions
        distributions = MedicationDistribution.objects.filter(
            prescription=prescription,
            pk__gt=self.pk  # Distributions after this one
        ).order_by('pk')
        
        # Recalculate remaining for subsequent distributions
        for dist in distributions:
            dist.remaining += amount
            dist.save(update_fields=['remaining'])

class DrugQuota(models.Model):
    """
    مدل سهمیه دارویی بیماران
    برای مدیریت سهمیه ماهانه هر بیمار برای هر نوع دارو استفاده می‌شود
    """
    patient = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE,
        verbose_name="بیمار",
        related_name='drug_quotas'
    )
    medication_type = models.ForeignKey(
        'MedicationType',
        on_delete=models.CASCADE,
        verbose_name="نوع دارو",
        related_name='patient_quotas'
    )
    monthly_quota = models.DecimalField(
        "سهمیه ماهانه",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, "مقدار سهمیه باید بزرگتر از صفر باشد")]
    )
    remaining_quota = models.DecimalField(
        "سهمیه باقی‌مانده",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0, "سهمیه باقی‌مانده نمی‌تواند منفی باشد")]
    )
    start_date = jmodels.jDateField("تاریخ شروع سهمیه")
    end_date = jmodels.jDateField("تاریخ پایان سهمیه")
    is_active = models.BooleanField("فعال", default=True)
    created_at = jmodels.jDateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = jmodels.jDateTimeField("تاریخ به‌روزرسانی", auto_now=True)
    
    class Meta:
        verbose_name = "سهمیه دارو"
        verbose_name_plural = "سهمیه‌های دارویی"
        unique_together = ('patient', 'medication_type', 'start_date')
        ordering = ['-start_date', 'medication_type__name']
        indexes = [
            models.Index(fields=['patient', 'medication_type']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"سهمیه {self.patient} - {self.medication_type.name}"
    
    def clean(self):
        # Validate remaining quota doesn't exceed monthly quota
        if self.remaining_quota > self.monthly_quota:
            raise ValidationError({
                'remaining_quota': 'سهمیه باقی‌مانده نمی‌تواند از سهمیه ماهانه بیشتر باشد'
            })
        
        # Validate date range
        if self.start_date > self.end_date:
            raise ValidationError('تاریخ پایان باید بعد از تاریخ شروع باشد')
        
        # Check for overlapping quotas
        overlapping_quotas = DrugQuota.objects.filter(
            patient=self.patient,
            medication_type=self.medication_type,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
            is_active=True
        ).exclude(pk=self.pk if self.pk else None)
        
        if overlapping_quotas.exists():
            raise ValidationError('بازه زمانی این سهمیه با سهمیه‌های دیگر همپوشانی دارد')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        # If this is a new quota and remaining_quota is not set, set it to monthly_quota
        if not self.pk and self.remaining_quota is None:
            self.remaining_quota = self.monthly_quota
        super().save(*args, **kwargs)

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

class Alert(models.Model):
    """
    مدل هشدارهای سیستم
    برای مدیریت هشدارهای مختلف سیستم استفاده می‌شود
    """
    ALERT_TYPES = [
        ('prescription_expiry', 'انقضای نسخه'),
        ('low_stock', 'موجودی کم'),
        ('quota_warning', 'هشدار سهمیه'),
        ('appointment', 'نوبت ویزیت'),
        ('other', 'سایر'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
        ('critical', 'بحرانی'),
    ]

    alert_type = models.CharField(
        "نوع هشدار",
        max_length=50,
        choices=ALERT_TYPES
    )
    title = models.CharField("عنوان هشدار", max_length=200)
    message = models.TextField("پیام هشدار")
    related_model = models.CharField(
        "مدل مرتبط",
        max_length=100,
        null=True,
        blank=True
    )
    related_id = models.PositiveIntegerField(
        "شناسه رکورد مرتبط",
        null=True,
        blank=True
    )
    priority = models.CharField(
        "اولویت",
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    is_read = models.BooleanField("خوانده شده", default=False)
    alert_date = jmodels.jDateTimeField("تاریخ هشدار", auto_now_add=True)
    due_date = jmodels.jDateTimeField("تاریخ موعد", null=True, blank=True)
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="ایجاد کننده"
    )

    class Meta:
        verbose_name = "هشدار"
        verbose_name_plural = "هشدارها"
        ordering = ['-alert_date']
        indexes = [
            models.Index(fields=['alert_type', 'is_read']),
            models.Index(fields=['related_model', 'related_id']),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()}: {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
        return True


# Signal handlers
@receiver(post_save, sender=MedicationDistribution)
def update_inventory_on_distribution(sender, instance, created, **kwargs):
    """
    Signal handler to update inventory when a distribution is saved
    """
    if created:
        inventory = instance.prescription.medication_type.inventory
        previous_stock = inventory.current_stock
        inventory.current_stock -= instance.amount
        inventory.save()
        
        # Log the inventory change
        InventoryLog.objects.create(
            inventory_item=inventory,
            quantity_change=-instance.amount,
            previous_quantity=previous_stock,
            new_quantity=inventory.current_stock,
            log_type='distribution',
            reference_type='medicationdistribution',
            reference_id=instance.id,
            created_by=instance.created_by,
            notes=f'توزیع برای بیمار {instance.prescription.patient}'
        )
        
        # Update patient's quota
        try:
            quota = DrugQuota.objects.filter(
                patient=instance.prescription.patient,
                medication_type=instance.prescription.medication_type,
                start_date__lte=instance.distribution_date,
                end_date__gte=instance.distribution_date,
                is_active=True
            ).first()
            
            if quota and quota.remaining_quota >= instance.amount:
                quota.remaining_quota -= instance.amount
                quota.save()
            elif quota:
                # Log quota violation but don't fail the transaction
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Insufficient quota for patient {instance.prescription.patient_id} "
                    f"for medication {instance.prescription.medication_type_id}"
                )
                
        except DrugQuota.DoesNotExist:
            # No active quota found, log but don't fail
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"No active quota found for patient {instance.prescription.patient_id} "
                f"and medication {instance.prescription.medication_type_id}"
            )

@receiver(post_delete, sender=MedicationDistribution)
def revert_inventory_on_distribution_delete(sender, instance, **kwargs):
    """
    Signal handler to revert inventory when a distribution is deleted
    """
    try:
        inventory = instance.prescription.medication_type.inventory
        previous_stock = inventory.current_stock
        inventory.current_stock += instance.amount
        inventory.save()
        
        # Log the inventory change
        InventoryLog.objects.create(
            inventory_item=inventory,
            quantity_change=instance.amount,
            previous_quantity=previous_stock,
            new_quantity=inventory.current_stock,
            log_type='return',
            reference_type='medicationdistribution',
            reference_id=instance.id,
            notes=f'عودت توزیع حذف شده برای بیمار {instance.prescription.patient}'
        )
        
        # Revert patient's quota
        try:
            quota = DrugQuota.objects.filter(
                patient=instance.prescription.patient,
                medication_type=instance.prescription.medication_type,
                start_date__lte=instance.distribution_date,
                end_date__gte=instance.distribution_date
            ).first()
            
            if quota:
                quota.remaining_quota += instance.amount
                quota.save()
                
        except DrugQuota.DoesNotExist:
            pass
            
    except DrugInventory.DoesNotExist:
        pass
