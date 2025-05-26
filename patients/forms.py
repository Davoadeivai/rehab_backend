from django import forms
from .models import Patient
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

# Example of using JalaliDate in a form field
# JalaliDate is a class from the khayyam library that converts Gregorian dates to Jalali dates
# and vice versa. You can use it to set the initial value of a form field to the current date in Jalali format.

class MyForm(forms.Form):
    date = forms.CharField(initial=jdatetime.date.today().strftime('%Y/%m/%d'))
