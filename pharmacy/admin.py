from .models import Supplier, Drug, DrugInventory, DrugPurchase, DrugSale, PrescriptionItem, InventoryLog
from django.contrib import admin
from django.contrib.auth.models import Group, Permission

# Register your models here.
admin.site.register(Supplier)
admin.site.register(Drug)
admin.site.register(DrugInventory)
admin.site.register(DrugPurchase)
admin.site.register(DrugSale)
admin.site.register(PrescriptionItem)
admin.site.register(InventoryLog)
