from django.db import models
from patients.medication_models import Prescription

# Create your models here.

class Supplier(models.Model):
    name = models.CharField('نام تامین‌کننده', max_length=255)
    contact_info = models.TextField('اطلاعات تماس', blank=True)
    address = models.TextField('آدرس', blank=True)
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'تامین‌کننده'
        verbose_name_plural = 'تامین‌کنندگان'

class Drug(models.Model):
    name = models.CharField('نام دارو', max_length=255)
    category = models.CharField('دسته', max_length=100, blank=True)
    description = models.TextField('توضیحات', blank=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='تامین‌کننده', default=1)
    price = models.DecimalField('قیمت', max_digits=10, decimal_places=2)
    expiration_date = models.DateField('تاریخ انقضا', null=True, blank=True)
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'دارو'
        verbose_name_plural = 'داروها'

class DrugInventory(models.Model):
    drug = models.OneToOneField(Drug, on_delete=models.CASCADE, verbose_name='دارو')
    quantity = models.PositiveIntegerField('موجودی', default=0)
    last_updated = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    def __str__(self):
        return f"{self.drug.name} - {self.quantity}"

    class Meta:
        verbose_name = 'موجودی دارو'
        verbose_name_plural = 'موجودی داروها'

class DrugPurchase(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, verbose_name='دارو')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='تامین‌کننده')
    quantity = models.PositiveIntegerField('تعداد')
    purchase_price = models.DecimalField('قیمت خرید', max_digits=10, decimal_places=2)
    purchase_date = models.DateField('تاریخ خرید', auto_now_add=True)
    purchase_datetime = models.DateTimeField('زمان دقیق خرید', auto_now_add=True, null=True)
    interval_days = models.PositiveIntegerField('بازه زمانی دریافت (روز)', null=True, blank=True)
    total_cost = models.DecimalField('مبلغ کل خرید', max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"خرید {self.drug.name} - {self.quantity} عدد"

    class Meta:
        verbose_name = 'خرید دارو'
        verbose_name_plural = 'خریدهای دارو'

class DrugSale(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, verbose_name='دارو')
    quantity = models.PositiveIntegerField('تعداد')
    sale_price = models.DecimalField('قیمت فروش', max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField('تاریخ فروش', auto_now_add=True)
    patient_name = models.CharField('نام بیمار', max_length=255, blank=True)
    prescription = models.ForeignKey('patients.Prescription', on_delete=models.SET_NULL, null=True, blank=True, related_name='drug_sales', verbose_name='نسخه')

    def __str__(self):
        return f"فروش {self.drug.name} - {self.quantity} عدد"

    class Meta:
        verbose_name = 'فروش دارو'
        verbose_name_plural = 'فروش‌های دارو'

class PrescriptionItem(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, verbose_name='دارو')
    prescription_id = models.IntegerField('کد نسخه')
    quantity = models.PositiveIntegerField('تعداد')
    instructions = models.TextField('دستور مصرف', blank=True)

    def __str__(self):
        return f"{self.drug.name} - نسخه {self.prescription_id}"

    class Meta:
        verbose_name = 'آیتم نسخه'
        verbose_name_plural = 'آیتم‌های نسخه'

class InventoryLog(models.Model):
    ACTION_CHOICES = [
        ('purchase', 'خرید'),
        ('sale', 'فروش'),
        ('manual', 'اصلاح دستی'),
    ]
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, verbose_name='دارو')
    action = models.CharField('نوع عملیات', max_length=20, choices=ACTION_CHOICES)
    quantity = models.DecimalField('مقدار', max_digits=10, decimal_places=2)
    date = models.DateTimeField('تاریخ', auto_now_add=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='کاربر', related_name='pharmacy_inventory_logs')
    note = models.TextField('توضیحات', blank=True)

    def __str__(self):
        return f"{self.drug.name} - {self.get_action_display()} - {self.quantity}"

    class Meta:
        verbose_name = 'تاریخچه موجودی'
        verbose_name_plural = 'تاریخچه‌های موجودی'

# لیست داروهای اولیه برای اضافه شدن به داروخانه
INITIAL_DRUGS = [
    {"name": "شربت اپیوم", "category": "شربت", "description": "", "price": 0},
    {"name": "قرص بوپرنورفین ۸ میلی‌گرم", "category": "قرص", "description": "", "price": 0},
    {"name": "قرص بوپرنورفین ۲ میلی‌گرم", "category": "قرص", "description": "", "price": 0},
    {"name": "قرص بوپرنورفین ۰.۴ میلی‌گرم", "category": "قرص", "description": "", "price": 0},
    {"name": "قرص متادون ۴۰ میلی‌گرم", "category": "قرص", "description": "", "price": 0},
    {"name": "قرص متادون ۲۰ میلی‌گرم", "category": "قرص", "description": "", "price": 0},
    {"name": "قرص متادون ۵ میلی‌گرم", "category": "قرص", "description": "", "price": 0},
    {"name": "شربت متادون", "category": "شربت", "description": "", "price": 0},
]
