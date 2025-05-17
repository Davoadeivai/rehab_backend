from django import forms
from .models import Patient, Family, Medication

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name']