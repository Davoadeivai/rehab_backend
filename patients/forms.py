from django import forms
from .models import Patient, Family, Medication

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
       
class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = '__all__'
        #  widgets = {
        #     'نام': forms.TextInput(attrs={'class': 'form-control'}),
        #     'نسبت': forms.TextInput(attrs={'class': 'form-control'}),
        #     'شماره_تماس': forms.TextInput(attrs={'class': 'form-control'}),
        # }
         
class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = '__all__'
        #  widgets = {
        #     'نام_دارو': forms.TextInput(attrs={'class': 'form-control'}),
        #     'دوز': forms.TextInput(attrs={'class': 'form-control'}),
        #     'تاریخ_شروع': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        #     'تاریخ_پایان': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        # }