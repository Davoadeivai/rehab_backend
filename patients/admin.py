from django.contrib import admin
from .models import Patient, Family, Medication

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'file_number',  'system_code', 'doctor_name', 'payment_amount', 'receiver_signature')

@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('patient', 'members_count', 'support_type')

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'dosage_40mg', 'dosage_20mg', 'dosage_5mg')
