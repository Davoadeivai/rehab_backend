from django import forms
from .models import Patient, Notification, Contact, Support, Feedback
from .medication_models import Service, ServiceTransaction, Payment, Prescription, MedicationDistribution, Medication, MedicationAdministration
import jdatetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
import re

import datetime

class JalaliDateField(forms.CharField):
    def __init__(self, *args, **kwargs):
        # Only set initial date if not provided and field is not required
        if 'initial' not in kwargs and not kwargs.get('required', True):
            kwargs['initial'] = ''
        elif 'initial' not in kwargs:
            kwargs['initial'] = jdatetime.date.today().strftime('%Y/%m/%d')
            
        super().__init__(*args, **kwargs)
        
        # Set widget attributes
        self.widget = forms.TextInput(attrs={
            'class': 'form-control date-input',
            'dir': 'ltr',
            'placeholder': 'مثال: 1402/01/01',
            'autocomplete': 'on'
        })

    def to_python(self, value):
        """
        Convert the input value to a Python date object.
        Returns None for empty values or invalid dates.
        """
        value = super().to_python(value)
        if not value:
            return None
        try:
            # Replace all non-digit with /
            value = re.sub(r'[^\d]', '/', value)
            # Extract year, month, day
            match = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})$', value)
            if not match:
                return value  # Let validation handle error
            year, month, day = map(int, match.groups())
            jalali_date = jdatetime.date(year, month, day)
            gregorian_date = jalali_date.togregorian()
            return gregorian_date
        except Exception:
            return value

    def validate(self, value):
        """
        Validate that the input can be converted to a valid date.
        """
        super().validate(value)
        
        # Skip validation for empty values if field is not required
        if not value and not self.required:
            return
            
        # If value is already a date object, it's already valid
        if isinstance(value, (jdatetime.date, datetime.date)):
            return
            
        # Handle string input
        if isinstance(value, str):
            try:
                # Try to parse the date string
                year, month, day = map(int, value.split('/'))
                jdatetime.date(year, month, day)
            except (ValueError, AttributeError) as e:
                raise ValidationError(
                    'لطفاً یک تاریخ معتبر به فرمت شمسی وارد کنید (مثال: 1402/01/01)',
                    code='invalid_date'
                )

    def clean_admission_date(self):
        date_str = self.cleaned_data.get('admission_date')
        if not date_str:
            raise forms.ValidationError("این فیلد اجباری است.")
        try:
            if isinstance(date_str, (datetime.date, jdatetime.date)):
                return date_str if isinstance(date_str, jdatetime.date) else jdatetime.date.fromgregorian(date=date_str)
            # Replace all non-digit with /
            date_str = re.sub(r'[^\d]', '/', str(date_str))
            match = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})$', date_str)
            if not match:
                raise ValueError
            year, month, day = map(int, match.groups())
            jalali_date = jdatetime.date(year, month, day)
            return jalali_date
        except Exception:
            raise forms.ValidationError("تاریخ نامعتبر است. لطفاً تاریخ را به فرمت صحیح شمسی (مثال: 1402/01/01) وارد کنید.")

    def clean_date_birth(self):
        date_str = self.cleaned_data.get('date_birth')
        if not date_str:
            raise forms.ValidationError("این فیلد اجباری است.")
        try:
            if isinstance(date_str, (datetime.date, jdatetime.date)):
                return date_str if isinstance(date_str, jdatetime.date) else jdatetime.date.fromgregorian(date=date_str)
            date_str = re.sub(r'[^\d]', '/', str(date_str))
            match = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})$', date_str)
            if not match:
                raise ValueError
            year, month, day = map(int, match.groups())
            jalali_date = jdatetime.date(year, month, day)
            return jalali_date
        except Exception:
            raise forms.ValidationError("تاریخ نامعتبر است. لطفاً تاریخ را به فرمت صحیح شمسی (مثال: 1402/01/01) وارد کنید.")

    def clean_treatment_withdrawal_date(self):
        date_str = self.cleaned_data.get('treatment_withdrawal_date')
        if not date_str:
            return None
        try:
            date_str = re.sub(r'[^\d]', '/', str(date_str))
            match = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})$', date_str)
            if not match:
                raise ValueError
            year, month, day = map(int, match.groups())
            jalali_date = jdatetime.date(year, month, day)
            return jalali_date
        except Exception:
            raise forms.ValidationError("تاریخ نامعتبر است. لطفاً تاریخ را به فرمت صحیح وارد کنید (مثال: 1402/01/01)")

class PatientForm(forms.ModelForm):
    date_birth = JalaliDateField(label='تاریخ تولد')
    admission_date = JalaliDateField(label='تاریخ پذیرش')
    treatment_withdrawal_date = JalaliDateField(label='تاریخ ترک درمان', required=False)

    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'national_code': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'education': forms.Select(attrs={'class': 'form-select'}),
            'drug_type': forms.Select(attrs={'class': 'form-select'}),
            'treatment_type': forms.Select(attrs={'class': 'form-select'}),
            'usage_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'file_number': forms.HiddenInput(attrs={'id': 'file_number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set empty labels
        self.fields['gender'].empty_label = "انتخاب کنید"
        self.fields['marital_status'].empty_label = "انتخاب کنید"
        self.fields['education'].empty_label = "انتخاب کنید"
        self.fields['drug_type'].empty_label = "انتخاب کنید"
        self.fields['treatment_type'].empty_label = "انتخاب کنید"
        
        # مقداردهی اولیه شماره پرونده به صورت یکتا
        if not self.instance.pk:
            today = jdatetime.date.today()
            self.initial['admission_date'] = today.strftime('%Y/%m/%d')
            # تولید شماره پرونده یکتا
            last_patient = Patient.objects.order_by('-file_number').first()
            last_number = int(last_patient.file_number) if last_patient and last_patient.file_number.isdigit() else 0
            new_file_number = str(last_number + 1).zfill(5)
            # اگر شماره تکراری بود، یک شماره جدید پیدا کن
            while Patient.objects.filter(file_number=new_file_number).exists():
                last_number += 1
                new_file_number = str(last_number + 1).zfill(5)
            self.initial['file_number'] = new_file_number

    def clean_file_number(self):
        file_number = self.cleaned_data.get('file_number')
        if not file_number:
            raise forms.ValidationError('شماره پرونده الزامی است.')
        qs = Patient.objects.filter(file_number=file_number)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('شماره پرونده تکراری است. لطفاً شماره دیگری وارد کنید.')
        return file_number

    def clean_admission_date(self):
        date_str = self.cleaned_data.get('admission_date')
        if not date_str:
            raise forms.ValidationError("این فیلد اجباری است.")
        try:
            if isinstance(date_str, (datetime.date, jdatetime.date)):
                return date_str if isinstance(date_str, jdatetime.date) else jdatetime.date.fromgregorian(date=date_str)
            # Replace all non-digit with /
            date_str = re.sub(r'[^\d]', '/', str(date_str))
            match = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})$', date_str)
            if not match:
                raise ValueError
            year, month, day = map(int, match.groups())
            jalali_date = jdatetime.date(year, month, day)
            return jalali_date
        except Exception:
            raise forms.ValidationError("تاریخ نامعتبر است. لطفاً تاریخ را به فرمت صحیح شمسی (مثال: 1402/01/01) وارد کنید.")

    def clean_date_birth(self):
        date_str = self.cleaned_data.get('date_birth')
        if not date_str:
            raise forms.ValidationError("این فیلد اجباری است.")
        try:
            if isinstance(date_str, (datetime.date, jdatetime.date)):
                return date_str if isinstance(date_str, jdatetime.date) else jdatetime.date.fromgregorian(date=date_str)
            date_str = re.sub(r'[^\d]', '/', str(date_str))
            match = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})$', date_str)
            if not match:
                raise ValueError
            year, month, day = map(int, match.groups())
            jalali_date = jdatetime.date(year, month, day)
            return jalali_date
        except Exception:
            raise forms.ValidationError("تاریخ نامعتبر است. لطفاً تاریخ را به فرمت صحیح شمسی (مثال: 1402/01/01) وارد کنید.")

    def clean_treatment_withdrawal_date(self):
        date_str = self.cleaned_data.get('treatment_withdrawal_date')
        if not date_str:
            return None
        try:
            date_str = re.sub(r'[^\d]', '/', str(date_str))
            match = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})$', date_str)
            if not match:
                raise ValueError
            year, month, day = map(int, match.groups())
            jalali_date = jdatetime.date(year, month, day)
            return jalali_date
        except Exception:
            raise forms.ValidationError("تاریخ نامعتبر است. لطفاً تاریخ را به فرمت صحیح وارد کنید (مثال: 1402/01/01)")

    def clean(self):
        cleaned_data = super().clean()
        admission_date = cleaned_data.get('admission_date')
        withdrawal_date = cleaned_data.get('treatment_withdrawal_date')
        date_birth = cleaned_data.get('date_birth')

        # تبدیل رشته خالی به None برای فیلدهای اختیاری
        if withdrawal_date == '':
            cleaned_data['treatment_withdrawal_date'] = None
            withdrawal_date = None

        if withdrawal_date and admission_date and withdrawal_date < admission_date:
            raise ValidationError('تاریخ ترک درمان نمی‌تواند قبل از تاریخ پذیرش باشد')

        if admission_date and date_birth and admission_date < date_birth:
            raise ValidationError('تاریخ پذیرش نمی‌تواند قبل از تاریخ تولد باشد')

        return cleaned_data

class PaymentForm(forms.ModelForm):
    payment_date = JalaliDateField(label='تاریخ پرداخت')

    class Meta:
        model = Payment
        fields = ['patient', 'prescription', 'payment_date', 'amount', 'payment_type', 'transactions']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'prescription': forms.HiddenInput(),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'transactions': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

    def clean_payment_date(self):
        payment_date = self.cleaned_data.get('payment_date')
        if payment_date and payment_date > datetime.date.today():
            raise ValidationError("تاریخ پرداخت نمی‌تواند در آینده باشد.")
        return payment_date

class ServiceTransactionForm(forms.ModelForm):
    class Meta:
        model = ServiceTransaction
        fields = ['patient', 'service', 'quantity', 'date']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class PrescriptionForm(forms.ModelForm):
    start_date = JalaliDateField(label='تاریخ شروع')
    end_date = JalaliDateField(label='تاریخ پایان')

    class Meta:
        model = Prescription
        fields = ['patient', 'medication_type', 'daily_dose', 'treatment_duration', 
                 'start_date', 'end_date', 'total_prescribed', 'notes',
                 'weekly_quota', 'monthly_quota', 'allocated_amount', 'received_amount', 'remaining_quota', 'period_type']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'medication_type': forms.Select(attrs={'class': 'form-select'}),
            'daily_dose': forms.NumberInput(attrs={'class': 'form-control'}),
            'treatment_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_prescribed': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'weekly_quota': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_quota': forms.NumberInput(attrs={'class': 'form-control'}),
            'allocated_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'received_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'remaining_quota': forms.NumberInput(attrs={'class': 'form-control'}),
            'period_type': forms.Select(attrs={'class': 'form-select'}),
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
        fields = ['patient', 'medication', 'administration_date', 'dose', 'administered_quantity', 'cost', 'signature', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'medication': forms.Select(attrs={'class': 'form-select'}),
            'dose': forms.Select(attrs={'class': 'form-select'}),
            'administered_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'signature': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'امضاء دریافت‌کننده'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
