from django import forms
from .models import Patient, Family, Medication,SubstanceAbuseRecord
import jdatetime

import datetime

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'نام': forms.TextInput(attrs={'class': 'form-control'}),
            'نام_خانوادگی': forms.TextInput(attrs={'class': 'form-control'}),
            'شماره_ملی': forms.TextInput(attrs={'class': 'form-control'}),
            'شماره_تماس': forms.TextInput(attrs={'class': 'form-control'}),
            'آدرس': forms.Textarea(attrs={'class': 'form-control'}),
            'تاریخ_ثبت': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
       
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
        
class SubstanceAbuseRecordForm(forms.ModelForm):
    class Meta:
        model = SubstanceAbuseRecord
        fields = '__all__'
        widgets = {
            'File_number': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_code': forms.TextInput(attrs={'class': 'form-control'}),
            'age_patient': forms.TextInput(attrs={'class': 'form-control'}),
            'age_of_onset': forms.NumberInput(attrs={'class': 'form-control'}),
            'substance_type': forms.Select(attrs={'class': 'form-control'}),
            'Type_of_treatment': forms.TextInput(attrs={'class': 'form-control'}),
            'address_numberphone': forms.Textarea(attrs={'class': 'form-control'}),
            'created_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'updated_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
# Example of using JalaliDate in a form field
# JalaliDate is a class from the khayyam library that converts Gregorian dates to Jalali dates
# and vice versa. You can use it to set the initial value of a form field to the current date in Jalali format.

class MyForm(forms.Form):
    date = forms.CharField(initial=jdatetime.date.today().strftime('%Y/%m/%d'))
