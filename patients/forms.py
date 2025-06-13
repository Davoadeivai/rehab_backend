from django import forms
from .models import Patient, Contact, Support, Feedback
from .medication_models import Payment, Prescription, MedicationDistribution, Medication, MedicationAdministration
import jdatetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

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
    class Meta:
        model = Patient
        exclude = ['created_at', 'updated_at']
    admission_date = JalaliDateField(label='تاریخ پذیرش')
    treatment_withdrawal_date = JalaliDateField(label='تاریخ ترک درمان', required=False)
    date_birth = JalaliDateField(label='تاریخ تولد')

    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام بیمار را وارد کنید'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نام خانوادگی را وارد کنید'}),
            'national_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'کد ملی ۱۰ رقمی'}),
            'file_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره پرونده منحصر به فرد'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: ۰۹۱۲۳۴۵۶۷۸۹'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'آدرس دقیق محل سکونت'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'drug_type': forms.Select(attrs={'class': 'form-select'}),
            'treatment_type': forms.Select(attrs={'class': 'form-select'}),
            'usage_duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مدت زمان مصرف به ماه'}),
        }
        error_messages = {
            'national_code': {
                'unique': _("بیماری با این کد ملی قبلاً ثبت شده است."),
            },
            'file_number': {
                'unique': _("بیماری با این شماره پرونده قبلاً ثبت شده است."),
            },
            'education': {
                'required': _('لطفاً سطح تحصیلات را انتخاب کنید.'),
            },
            'marital_status': {
                'required': _('لطفاً وضعیت تأهل را انتخاب کنید.'),
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['education'].required = True
        self.fields['marital_status'].required = True
        self.fields['gender'].empty_label = "جنسیت را انتخاب کنید"
        self.fields['marital_status'].empty_label = "وضعیت تأهل را انتخاب کنید"
        self.fields['education'].empty_label = "سطح تحصیلات را انتخاب کنید"
        self.fields['drug_type'].empty_label = "نوع ماده مصرفی را انتخاب کنید"
        self.fields['treatment_type'].empty_label = "نوع درمان را انتخاب کنید"

        # Make file_number hidden so browser submits its value
        self.fields['file_number'].required = False
        self.fields['file_number'].widget = forms.HiddenInput()

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
        fields = ['patient', 'payment_date', 'amount', 'payment_period', 'description']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_period': forms.Select(attrs={'class': 'form-select'}),
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

class UserProfileForm(forms.ModelForm):
    """فرم ویرایش پروفایل کاربر"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class UserSettingsForm(forms.ModelForm):
    """فرم تنظیمات کاربر"""
    class Meta:
        model = User
        fields = ['username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ContactForm(forms.ModelForm):
    """فرم تماس با ما"""
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class SupportForm(forms.ModelForm):
    """فرم پشتیبانی فنی"""
    class Meta:
        model = Support
        fields = ['title', 'description', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

class FeedbackForm(forms.ModelForm):
    """فرم ارسال پیشنهادات"""
    class Meta:
        model = Feedback
        fields = ['title', 'description', 'type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MedicationAdministrationForm(forms.ModelForm):
    administration_date = JalaliDateField(label='تاریخ تجویز')

    class Meta:
        model = MedicationAdministration
        fields = ['patient', 'medication', 'administration_date', 'administered_quantity', 'cost', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'medication': forms.Select(attrs={'class': 'form-select'}),
            'administered_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
