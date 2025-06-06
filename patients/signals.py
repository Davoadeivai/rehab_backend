from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MedicationType, DrugInventory

@receiver(post_save, sender=MedicationType)
def create_inventory_for_new_medication(sender, instance, created, **kwargs):
    if created:
        DrugInventory.objects.create(medication_type=instance)