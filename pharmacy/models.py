from django.db import models
from patients.medication_models import Prescription

# Create your models here.

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Drug(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expiration_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DrugInventory(models.Model):
    drug = models.OneToOneField(Drug, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.drug.name} - {self.quantity}"

class DrugPurchase(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"خرید {self.drug.name} - {self.quantity} عدد"

class DrugSale(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    patient_name = models.CharField(max_length=255, blank=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True, related_name='drug_sales')

    def __str__(self):
        return f"فروش {self.drug.name} - {self.quantity} عدد"

class PrescriptionItem(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    prescription_id = models.IntegerField()  # ارتباط با مدل Prescription در صورت نیاز
    quantity = models.PositiveIntegerField()
    instructions = models.TextField(blank=True)

    def __str__(self):
        return f"{self.drug.name} - نسخه {self.prescription_id}"

class InventoryLog(models.Model):
    ACTION_CHOICES = [
        ('purchase', 'خرید'),
        ('sale', 'فروش'),
        ('manual', 'اصلاح دستی'),
    ]
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.drug.name} - {self.get_action_display()} - {self.quantity}"
