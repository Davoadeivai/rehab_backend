from django import forms
from .models import Patient, Family, Medication

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        #   widgets = {
        #     'تاریخ_تولد': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        # }