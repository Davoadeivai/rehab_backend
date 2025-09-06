from django import forms
from .models import Patient, Notification, Contact, Support, Feedback
from .medication_models import Service, ServiceTransaction, Payment, Prescription, MedicationDistribution, Medication, MedicationAdministration, PrescriptionItem, MedicationType
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
    treatment_withdrawal_date = JalaliDateField(
        label='تاریخ خروج از درمان',
        required=False,
        help_text='در صورت اتمام درمان، تاریخ خروج را وارد کنید',
        widget=forms.TextInput(attrs={
            'class': 'form-control date-input',
            'dir': 'ltr',
            'placeholder': 'مثال: 1402/01/01',
            'autocomplete': 'off'
        })
    )

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
        
        # Make file_number field editable
        self.fields['file_number'].required = True
        self.fields['file_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'شماره پرونده را وارد کنید',
            'dir': 'ltr'
        })
        
        # Remove the auto-generated file number
        if not self.instance.pk:
            today = jdatetime.date.today()
            self.initial['admission_date'] = today.strftime('%Y/%m/%d')

    def clean_file_number(self):
        file_number = self.cleaned_data.get('file_number')
        if not file_number:
            raise ValidationError("شماره پرونده الزامی است.")
        if not file_number.isdigit():
            raise ValidationError("شماره پرونده باید فقط شامل اعداد باشد.")
        if Patient.objects.filter(file_number=file_number).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError("این شماره پرونده قبلاً ثبت شده است.")
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

class PrescriptionItemForm(forms.ModelForm):
    """Form for individual prescription items (drugs)"""
    medication = forms.ModelChoiceField(
        queryset=MedicationType.objects.all(),
        label='دارو',
        widget=forms.Select(attrs={'class': 'form-select select2-medicine'})
    )
    
    class Meta:
        model = PrescriptionItem
        fields = [
            'medication', 'dosage', 'dosage_unit', 'frequency', 'route', 
            'duration', 'instructions', 'is_prn', 'prn_instructions', 'start_date'
        ]
        widgets = {
            'dosage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'مقدار مصرف'
            }),
            'dosage_unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثلاً: عدد، میلی‌گرم، سی‌سی'
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'تعداد دفعات مصرف در روز'
            }),
            'route': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'راه مصرف را انتخاب کنید'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مدت مصرف به روز'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'دستورات مصرف (اختیاری)'
            }),
            'prn_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'دستورالعمل مصرف در صورت نیاز (اختیاری)'
            }),
            'start_date': JalaliDateField(
                label='تاریخ شروع مصرف',
                required=False,
                help_text='در صورت خالی بودن، تاریخ شروع نسخه در نظر گرفته می‌شود'
            ).widget
        }
        help_texts = {
            'dosage': 'مقدار مصرف در هر نوبت',
            'duration': 'مدت زمان مصرف به روز',
            'is_prn': 'در صورت فعال بودن، این دارو فقط در صورت نیاز مصرف می‌شود',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        self.fields['dosage_unit'].initial = 'عدد'
        self.fields['frequency'].initial = 'bid'  # Twice a day
        self.fields['route'].initial = 'po'  # Oral


PrescriptionItemFormSet = forms.inlineformset_factory(
    Prescription, 
    PrescriptionItem, 
    form=PrescriptionItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)


class PrescriptionForm(forms.ModelForm):
    start_date = JalaliDateField(
        label='تاریخ شروع',
        help_text='تاریخ شروع مصرف دارو را وارد کنید'
    )
    end_date = JalaliDateField(
        label='تاریخ پایان',
        help_text='تاریخ پایان مصرف دارو را وارد کنید',
        required=False
    )

    class Meta:
        model = Prescription
        fields = [
            'patient', 'prescription_type', 'priority', 'doctor', 'doctor_code',
            'medication_type', 'daily_dose', 'treatment_duration', 'start_date',
            'end_date', 'total_prescribed', 'diagnosis', 'notes', 'weekly_quota',
            'monthly_quota', 'allocated_amount', 'period_type'
        ]
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'انتخاب بیمار'
            }),
            'prescription_type': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'نوع نسخه را انتخاب کنید'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'اولویت را انتخاب کنید'
            }),
            'doctor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نام پزشک معالج'
            }),
            'doctor_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'کد نظام پزشکی',
                'data-mask': '0000000'
            }),
            'medication_type': forms.Select(attrs={
                'class': 'form-select select2-medicine',
                'data-placeholder': 'نوع دارو را انتخاب کنید'
            }),
            'daily_dose': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'مقدار مصرف روزانه'
            }),
            'treatment_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مدت درمان به روز'
            }),
            'total_prescribed': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'tabindex': '-1'
            }),
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'تشخیص پزشکی (اختیاری)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'دستورات و توضیحات تکمیلی (اختیاری)'
            }),
            'weekly_quota': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'سهمیه هفتگی'
            }),
            'monthly_quota': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'سهمیه ماهانه'
            }),
            'allocated_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'مقدار تخصیص یافته'
            }),
            'period_type': forms.Select(attrs={
                'class': 'form-select',
                'data-placeholder': 'نوع بازه سهمیه را انتخاب کنید'
            }),
        }
        help_texts = {
            'prescription_type': 'نوع نسخه را مشخص کنید',
            'priority': 'اولویت نسخه را تعیین کنید',
            'doctor': 'نام پزشک معالج را وارد کنید',
            'doctor_code': 'کد نظام پزشکی پزشک معالج را وارد کنید',
            'diagnosis': 'تشخیص پزشکی مربوط به این نسخه',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set default values
        if not self.instance.pk:
            self.fields['prescription_type'].initial = 'normal'
            self.fields['priority'].initial = 'medium'
            self.fields['period_type'].initial = 'week'
            
            # Set current user as created_by
            if self.user and self.user.is_authenticated:
                self.fields['created_by'] = forms.ModelChoiceField(
                    queryset=User.objects.filter(pk=self.user.pk),
                    initial=self.user.pk,
                    widget=forms.HiddenInput()
                )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        treatment_duration = cleaned_data.get('treatment_duration')
        daily_dose = cleaned_data.get('daily_dose')
        
        # Calculate end date if not provided
        if start_date and treatment_duration and not end_date:
            end_date = start_date + datetime.timedelta(days=treatment_duration)
            cleaned_data['end_date'] = end_date
        
        # Calculate total prescribed if daily_dose and treatment_duration are provided
        if daily_dose and treatment_duration:
            cleaned_data['total_prescribed'] = daily_dose * treatment_duration
            
        # Validate dates
        if start_date and end_date and end_date < start_date:
            raise ValidationError('تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد')
            
        # Set created_by if not set
        if not self.instance.pk and not cleaned_data.get('created_by') and hasattr(self, 'user') and self.user.is_authenticated:
            cleaned_data['created_by'] = self.user
            
        return cleaned_data

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
