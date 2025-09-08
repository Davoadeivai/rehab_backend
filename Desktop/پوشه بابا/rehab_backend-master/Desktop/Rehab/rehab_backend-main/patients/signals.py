from django.db.models.signals import post_save
from django.dispatch import receiver
from .medication_models import MedicationType, DrugInventory, Prescription
from pharmacy.models import Drug, DrugSale, DrugInventory as PharmacyDrugInventory, InventoryLog
from django.contrib.auth import get_user_model
from decimal import Decimal

@receiver(post_save, sender=MedicationType)
def create_inventory_for_new_medication(sender, instance, created, **kwargs):
    if created:
        DrugInventory.objects.create(medication_type=instance)

# --- ثبت خودکار فروش دارو و کسر موجودی هنگام ثبت نسخه جدید ---
@receiver(post_save, sender=Prescription)
def create_drug_sale_for_prescription(sender, instance, created, **kwargs):
    if not created:
        return
    # پیدا کردن داروی معادل در داروخانه بر اساس نام
    try:
        drug = Drug.objects.get(name=instance.medication_type.name)
    except Drug.DoesNotExist:
        # اگر دارو در داروخانه وجود ندارد، ثبت نشود
        return
    # مقدار داروی تجویز شده
    quantity = int(instance.total_prescribed)
    # قیمت فروش (می‌توانید قیمت را از مدل Drug بگیرید یا مقدار ثابت قرار دهید)
    sale_price = drug.price * quantity
    # نام بیمار
    patient_name = f"{instance.patient.first_name} {instance.patient.last_name}"
    # موجودی داروخانه
    try:
        inventory = PharmacyDrugInventory.objects.get(drug=drug)
    except PharmacyDrugInventory.DoesNotExist:
        return
    if inventory.quantity < quantity:
        # موجودی کافی نیست، ثبت نشود
        return
    # ثبت فروش دارو
    DrugSale.objects.create(
        drug=drug,
        quantity=quantity,
        sale_price=sale_price,
        patient_name=patient_name,
        prescription=instance
    )
    # کسر موجودی
    inventory.quantity -= quantity
    inventory.save()
    # ثبت لاگ
    InventoryLog.objects.create(
        drug=drug,
        action='sale',
        quantity=Decimal(quantity),
        user=None,
        note=f'فروش اتوماتیک به بیمار: {patient_name} (ثبت نسخه جدید)'
    )