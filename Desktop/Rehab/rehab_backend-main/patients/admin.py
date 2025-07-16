from django.contrib import admin
from .models import Patient, Contact, Support, Feedback
from .medication_models import (
    MedicationType, Prescription, MedicationDistribution, Payment,
    Service, ServiceTransaction, DrugDispenseHistory
)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('file_number', 'first_name', 'last_name',
                    'national_code', 'date_birth', 'gender',
                    'phone_number', 'address', 'marital_status',
                    'education', 'drug_type', 'treatment_type',
                    'usage_duration', 'admission_date',
                    'treatment_withdrawal_date')
    
    search_fields = ('file_number', 'first_name', 'last_name', 'national_code')

@admin.register(MedicationType)
class MedicationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'description')
    search_fields = ('name', 'description')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medication_type', 'daily_dose',
                   'treatment_duration', 'start_date', 'end_date',
                   'total_prescribed', 'weekly_quota', 'monthly_quota', 'allocated_amount', 'received_amount', 'remaining_quota', 'period_type')
    list_filter = ('medication_type', 'start_date', 'end_date', 'period_type')
    search_fields = ('patient__file_number', 'patient__first_name',
                    'patient__last_name', 'medication_type__name')
    date_hierarchy = 'start_date'

@admin.register(MedicationDistribution)
class MedicationDistributionAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'distribution_date', 'amount',
                   'remaining', 'created_at')
    list_filter = ('distribution_date', 'prescription__medication_type')
    search_fields = ('prescription__patient__file_number',
                    'prescription__patient__first_name',
                    'prescription__patient__last_name',
                    'prescription__medication_type__name')
    date_hierarchy = 'distribution_date'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'unit_price')
    list_filter = ('service_type',)
    search_fields = ('name', 'description')

@admin.register(ServiceTransaction)
class ServiceTransactionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'service', 'date', 'quantity', 'total_cost')
    list_filter = ('date', 'service__service_type')
    search_fields = ('patient__first_name', 'patient__last_name', 'service__name')
    date_hierarchy = 'date'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'payment_date', 'amount')
    list_filter = ('payment_date',)
    search_fields = ('patient__first_name', 'patient__last_name', 'description')
    date_hierarchy = 'payment_date'
    filter_horizontal = ('transactions',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    date_hierarchy = 'created_at'

@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'created_at', 'is_resolved')
    list_filter = ('priority', 'is_resolved', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'created_at', 'is_read')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

# --- new admin for DrugDispenseHistory ---
@admin.register(DrugDispenseHistory)
class DrugDispenseHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'prescription', 'medication_type', 'dispense_date', 'amount', 'period_type', 'period_label', 'remaining_quota', 'created_at')
    list_filter = ('medication_type', 'period_type', 'dispense_date')
    search_fields = ('patient__file_number', 'patient__first_name', 'patient__last_name', 'period_label')

    
                    
   

