from django.db import models
from django_jalali.db import models as jmodels
from django.utils import timezone
from django.core.exceptions import ValidationError

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
        # Calculate sum of amounts for existing distributions of the same prescription
        distributed_so_far = MedicationDistribution.objects.filter(prescription=prescription)
        if self.pk: # if updating, exclude current instance from sum
            distributed_so_far = distributed_so_far.exclude(pk=self.pk)

        # Summing up the 'amount' field from the queryset
        # For Django versions before 4.0, aggregate might be needed if direct sum() on queryset is not supported as efficiently
        # from django.db.models import Sum
        # total_previously_distributed = distributed_so_far.aggregate(total=Sum('amount'))['total'] or 0
        # Using a loop for clarity and compatibility, can be optimized with aggregate
        total_previously_distributed = sum(dist.amount for dist in distributed_so_far)

        if (total_previously_distributed + self.amount) > prescription.total_prescribed:
            raise ValidationError(
                f"مقدار توزیع شده ({total_previously_distributed + self.amount}) "
                f"بیشتر از مقدار کل تجویز شده ({prescription.total_prescribed}) است."
            )

        # Existing inventory management logic
        # This part should only run if the distribution is new (not an update)
        # and after all validations have passed.
        is_new_distribution = not self.pk

        if is_new_distribution:
            try:
                # Ensure medication_type and inventory are accessed correctly
                inventory = prescription.medication_type.inventory
                if inventory.current_stock >= self.amount:
                    inventory.current_stock -= self.amount
                    # inventory.save() will be called later if super().save() is successful
                    # However, if other parts of the system rely on inventory being saved immediately,
                    # this might need adjustment. For now, let's assume it's part of the transaction.
                else:
                    # Using ValidationError for consistency with other checks
                    raise ValidationError("موجودی کافی برای این دارو در انبار نیست.")
            except DrugInventory.DoesNotExist:
                raise ValidationError("موجودی برای این دارو تعریف نشده است.")
            except AttributeError: # Handles if prescription.medication_type.inventory is not found
                raise ValidationError("ساختار اطلاعاتی دارو یا انبار دارو صحیح نیست.")

        super().save(*args, **kwargs) # Original save call

        # If the distribution is new and super().save() was successful, save the inventory.
        # This makes the inventory change part of the successful save operation.
        if is_new_distribution:
            try:
                # Re-fetch to be safe, or assume inventory object is still valid
                inventory = prescription.medication_type.inventory
                inventory.save()
            except DrugInventory.DoesNotExist:
                # This should ideally not happen if it passed above, but as a safeguard
                raise ValidationError("موجودی برای این دارو تعریف نشده است (هنگام ذخیره نهایی انبار).")
            except AttributeError:
                 raise ValidationError("ساختار اطلاعاتی دارو یا انبار دارو صحیح نیست (هنگام ذخیره نهایی انبار).")


    def delete(self, *args, **kwargs):
        # برگرداندن موجودی هنگام حذف توزیع
        try:
            inventory = self.prescription.medication_type.inventory
            inventory.current_stock += self.amount
            inventory.save()
        except DrugInventory.DoesNotExist:
            pass
            
        super().delete(*args, **kwargs)

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