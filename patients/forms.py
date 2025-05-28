from django import forms
from .models import Patient, Payment, Prescription, MedicationDistribution
import jdatetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

import datetime

class JalaliDateField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.required = True
        self.widget = forms.TextInput(attrs={
            'class': 'form-control date-input',
            'dir': 'ltr',
            'placeholder': 'مثال: ۱۴۰۲/۰۱/۰۱'
        })

    def to_python(self, value):
        if not value:
            return None
        try:
            # تبدیل تاریخ از فرمت شمسی به میلادی
            year, month, day = map(int, value.split('/'))
            jalali_date = jdatetime.date(year, month, day)
            return jalali_date.togregorian()
        except (ValueError, TypeError):
            raise ValidationError('تاریخ وارد شده معتبر نیست. لطفاً تاریخ را به فرمت صحیح وارد کنید (مثال: ۱۴۰۲/۰۱/۰۱)')

class PatientForm(forms.ModelForm):
    admission_date = JalaliDateField(label='تاریخ پذیرش')
    treatment_withdrawal_date = JalaliDateField(label='تاریخ ترک درمان', required=False)
    date_birth = JalaliDateField(label='تاریخ تولد')

    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_code': forms.TextInput(attrs={'class': 'form-control'}),
            'file_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'education': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'drug_type': forms.Select(attrs={'class': 'form-select'}),
            'treatment_type': forms.Select(attrs={'class': 'form-select'}),
            'usage_duration': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'education': {
                'required': 'لطفاً سطح تحصیلات را انتخاب کنید',
            },
            'marital_status': {
                'required': 'لطفاً وضعیت تأهل را انتخاب کنید',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['education'].required = True
        self.fields['marital_status'].required = True
        
        # اضافه کردن پیام‌های خطای فارسی
        self.fields['education'].error_messages = {
            'required': 'لطفاً سطح تحصیلات را انتخاب کنید',
        }
        self.fields['marital_status'].error_messages = {
            'required': 'لطفاً وضعیت تأهل را انتخاب کنید',
        }

    def clean(self):
        cleaned_data = super().clean()
        admission_date = cleaned_data.get('admission_date')
        withdrawal_date = cleaned_data.get('treatment_withdrawal_date')
        date_birth = cleaned_data.get('date_birth')

        if withdrawal_date and admission_date and withdrawal_date < admission_date:
            raise ValidationError('تاریخ ترک درمان نمی‌تواند قبل از تاریخ پذیرش باشد')

        if admission_date and date_birth and admission_date < date_birth:
            raise ValidationError('تاریخ پذیرش نمی‌تواند قبل از تاریخ تولد باشد')

        return cleaned_data

class PaymentForm(forms.ModelForm):
    payment_date = JalaliDateField(label='تاریخ پرداخت')

    class Meta:
        model = Payment
        fields = ['patient', 'payment_date', 'amount', 'payment_type', 'description']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_payment_date(self):
        date = self.cleaned_data.get('payment_date')
        if not date:
            raise ValidationError('لطفاً تاریخ پرداخت را وارد کنید')
        return date

class PrescriptionForm(forms.ModelForm):
    start_date = JalaliDateField(label='تاریخ شروع')
    end_date = JalaliDateField(label='تاریخ پایان')

    class Meta:
        model = Prescription
        fields = ['patient', 'medication_type', 'daily_dose', 'treatment_duration', 
                 'start_date', 'end_date', 'total_prescribed', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'medication_type': forms.Select(attrs={'class': 'form-select'}),
            'daily_dose': forms.NumberInput(attrs={'class': 'form-control'}),
            'treatment_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_prescribed': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise ValidationError('تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد')

        return cleaned_data

class MedicationDistributionForm(forms.ModelForm):
    distribution_date = JalaliDateField(label='تاریخ توزیع')

    class Meta:
        model = MedicationDistribution
        fields = ['prescription', 'distribution_date', 'amount', 'notes']
        widgets = {
            'prescription': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        prescription = cleaned_data.get('prescription')
        amount = cleaned_data.get('amount')
        distribution_date = cleaned_data.get('distribution_date')

        if prescription and amount:
            total_distributed = MedicationDistribution.objects.filter(
                prescription=prescription
            ).aggregate(total=models.Sum('amount'))['total'] or 0
            
            remaining = prescription.total_prescribed - (total_distributed + amount)
            if remaining < 0:
                raise ValidationError('مقدار توزیع شده بیشتر از مقدار تجویز شده است')

        if prescription and distribution_date:
            if distribution_date < prescription.start_date:
                raise ValidationError('تاریخ توزیع نمی‌تواند قبل از تاریخ شروع نسخه باشد')
            if distribution_date > prescription.end_date:
                raise ValidationError('تاریخ توزیع نمی‌تواند بعد از تاریخ پایان نسخه باشد')

        return cleaned_data
