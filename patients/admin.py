from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('file_number', 'first_name', 'last_name',
                    'national_code', 'date_birth', 'gender',
                    'phone_number', 'address', 'marital_status',
                    'education', 'drug_type', 'treatment_type',
                    'usage_duration', 'admission_date',
                    'treatment_withdrawal_date')
    
    search_fields = ('file_number', 'first_name', 'last_name', 'national_code')

    
                    
   

