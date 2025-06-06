from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Patient, MedicationType, Prescription, MedicationDistribution, Payment
from datetime import date
import jdatetime

class PatientViewSetTests(APITestCase):
    """تست‌های مربوط به ویوست بیماران"""

    def setUp(self):
        """راه‌اندازی داده‌های اولیه برای تست"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.patient_data = {
            'file_number': 'TEST001',
            'first_name': 'تست',
            'last_name': 'تستی',
            'national_code': '1234567890',
            'date_birth': '1370-01-01',
            'gender': 'M',
            'marital_status': 'S',
            'education': 'D',
            'drug_type': 'H',
            'treatment_type': 'MMT',
            'admission_date': '1402-01-01'
        }
        
        self.patient = Patient.objects.create(**self.patient_data)

    def test_create_patient(self):
        """تست ایجاد بیمار جدید"""
        url = reverse('patient-list')
        new_patient_data = self.patient_data.copy()
        new_patient_data['file_number'] = 'TEST002'
        new_patient_data['national_code'] = '0987654321'
        
        response = self.client.post(url, new_patient_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patient.objects.count(), 2)
        self.assertEqual(Patient.objects.get(file_number='TEST002').national_code, '0987654321')

    def test_get_patient_list(self):
        """تست دریافت لیست بیماران"""
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_patient_detail(self):
        """تست دریافت جزئیات بیمار"""
        url = reverse('patient-detail', kwargs={'pk': self.patient.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['file_number'], 'TEST001')

    def test_update_patient(self):
        """تست به‌روزرسانی اطلاعات بیمار"""
        url = reverse('patient-detail', kwargs={'pk': self.patient.pk})
        updated_data = {'first_name': 'تست‌شده'}
        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Patient.objects.get(pk=self.patient.pk).first_name, 'تست‌شده')

class PrescriptionViewSetTests(APITestCase):
    """تست‌های مربوط به ویوست نسخه‌ها"""

    def setUp(self):
        """راه‌اندازی داده‌های اولیه برای تست"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.patient = Patient.objects.create(
            file_number='TEST001',
            first_name='تست',
            last_name='تستی',
            national_code='1234567890'
        )
        
        self.medication_type = MedicationType.objects.create(
            name='متادون',
            unit='میلی‌گرم'
        )
        
        self.prescription_data = {
            'patient': self.patient,
            'medication_type': self.medication_type,
            'daily_dose': 50,
            'total_prescribed': 1500,
            'start_date': '1402-01-01',
            'end_date': '1402-02-01'
        }
        
        self.prescription = Prescription.objects.create(**self.prescription_data)

    def test_create_prescription(self):
        """تست ایجاد نسخه جدید"""
        url = reverse('prescription-list')
        new_prescription_data = {
            'patient': self.patient.id,
            'medication_type': self.medication_type.id,
            'daily_dose': 60,
            'total_prescribed': 1800,
            'start_date': '1402-02-01',
            'end_date': '1402-03-01'
        }
        
        response = self.client.post(url, new_prescription_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Prescription.objects.count(), 2)

class MedicationDistributionViewSetTests(APITestCase):
    """تست‌های مربوط به ویوست توزیع دارو"""

    def setUp(self):
        """راه‌اندازی داده‌های اولیه برای تست"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.patient = Patient.objects.create(
            file_number='TEST001',
            first_name='تست',
            last_name='تستی'
        )
        
        self.medication_type = MedicationType.objects.create(
            name='متادون',
            unit='میلی‌گرم'
        )
        
        self.prescription = Prescription.objects.create(
            patient=self.patient,
            medication_type=self.medication_type,
            daily_dose=50,
            total_prescribed=1500,
            start_date='1402-01-01',
            end_date='1402-02-01'
        )

    def test_create_distribution(self):
        """تست ایجاد توزیع دارو"""
        url = reverse('medicationdistribution-list')
        distribution_data = {
            'prescription': self.prescription.id,
            'amount': 50,
            'distribution_date': '1402-01-01'
        }
        
        response = self.client.post(url, distribution_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MedicationDistribution.objects.count(), 1)

    def test_exceed_prescription_amount(self):
        """تست خطای توزیع بیش از مقدار تجویز شده"""
        url = reverse('medicationdistribution-list')
        distribution_data = {
            'prescription': self.prescription.id,
            'amount': 2000,  # بیشتر از مقدار تجویز شده
            'distribution_date': '1402-01-01'
        }
        
        response = self.client.post(url, distribution_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class PaymentViewSetTests(APITestCase):
    """تست‌های مربوط به ویوست پرداخت‌ها"""

    def setUp(self):
        """راه‌اندازی داده‌های اولیه برای تست"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.patient = Patient.objects.create(
            file_number='TEST001',
            first_name='تست',
            last_name='تستی'
        )

    def test_create_payment(self):
        """تست ایجاد پرداخت جدید"""
        url = reverse('payment-list')
        payment_data = {
            'patient': self.patient.id,
            'amount': 1000000,
            'payment_type': 'V',  # ویزیت
            'payment_date': '1402-01-01'
        }
        
        response = self.client.post(url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)

    def test_payment_summary(self):
        """تست گزارش خلاصه پرداخت‌ها"""
        # ایجاد چند پرداخت نمونه
        Payment.objects.create(
            patient=self.patient,
            amount=1000000,
            payment_type='V',
            payment_date='1402-01-01'
        )
        Payment.objects.create(
            patient=self.patient,
            amount=2000000,
            payment_type='M',  # دارو
            payment_date='1402-01-02'
        )
        
        url = reverse('payment-summary')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_count'], 2)
        self.assertEqual(response.data['total_amount'], 3000000)


from django.core.exceptions import ValidationError
from datetime import date, timedelta

class PatientValidationTests(TestCase):
    def setUp(self):
        self.valid_patient_data = {
            'file_number': 'VALID001',
            'first_name': 'Valid',
            'last_name': 'User',
            'national_code': '1234567890', # Valid
            'phone_number': '09123456789', # Valid
            'marital_status': Patient.MARITAL_STATUS_CHOICES[0][0], # Use first choice
            'education': Patient.EDUCATION_CHOICES[0][0],
            'treatment_type': Patient.TREATMENT_TYPE_CHOICES[0][0],
            'usage_duration': "1 year",
            'date_birth': date(1990, 1, 1),
            'admission_date': date(2023, 1, 1),
            'treatment_withdrawal_date': date(2023, 6, 1)
        }

    def create_patient(self, **kwargs):
        """Helper to create a patient instance with overridden data."""
        data = {**self.valid_patient_data, **kwargs}
        return Patient(**data)

    # National Code Tests
    def test_valid_national_code(self):
        patient = self.create_patient(national_code="0123456789")
        try:
            patient.save()  # Should not raise ValidationError
        except ValidationError:
            self.fail("Valid national code raised ValidationError.")

    def test_invalid_national_code_short(self):
        patient = self.create_patient(national_code="12345")
        with self.assertRaises(ValidationError, msg="کد ملی باید دقیقا ۱۰ رقم باشد."):
            patient.save()

    def test_invalid_national_code_long(self):
        patient = self.create_patient(national_code="12345678901")
        with self.assertRaises(ValidationError, msg="کد ملی باید دقیقا ۱۰ رقم باشد."):
            patient.save()

    def test_invalid_national_code_non_numeric(self):
        patient = self.create_patient(national_code="12345abcde")
        with self.assertRaises(ValidationError, msg="کد ملی باید فقط شامل اعداد باشد."):
            patient.save()

    def test_national_code_empty(self):
        # Based on Patient.save() logic, empty national_code is not explicitly checked before isdigit/len
        # However, model has national_code = models.CharField("کد ملی", max_length=10, unique=True)
        # which means it cannot be null. An empty string "" would fail len check.
        patient = self.create_patient(national_code="")
        with self.assertRaises(ValidationError, msg="کد ملی باید دقیقا ۱۰ رقم باشد."): # Or a different msg if empty check is specific
            patient.save()

    # Phone Number Tests
    def test_valid_phone_number(self):
        patient = self.create_patient(phone_number="09123456789")
        try:
            patient.save()
        except ValidationError:
            self.fail("Valid phone number raised ValidationError.")

    def test_invalid_phone_number_short(self):
        patient = self.create_patient(phone_number="0912345")
        with self.assertRaises(ValidationError, msg="شماره تلفن باید ۱۱ رقم باشد."):
            patient.save()

    def test_invalid_phone_number_long(self):
        patient = self.create_patient(phone_number="091234567890")
        with self.assertRaises(ValidationError, msg="شماره تلفن باید ۱۱ رقم باشد."):
            patient.save()

    def test_invalid_phone_number_non_numeric(self):
        patient = self.create_patient(phone_number="0912345abcd")
        with self.assertRaises(ValidationError, msg="شماره تلفن باید فقط شامل اعداد باشد."):
            patient.save()

    def test_phone_number_none(self):
        # Validation in save() is `if self.phone_number:`, so None should skip it.
        patient = self.create_patient(phone_number=None)
        try:
            patient.save() # Should not raise ValidationError from the custom checks
        except ValidationError:
            self.fail("Phone_number=None raised ValidationError unexpectedly.")

    def test_phone_number_empty(self):
        # Validation in save() is `if self.phone_number:`, so "" should skip it.
        patient = self.create_patient(phone_number="")
        try:
            patient.save() # Should not raise ValidationError from the custom checks
        except ValidationError:
            self.fail("Phone_number='' raised ValidationError unexpectedly.")


    # Date Consistency Tests
    def test_valid_dates(self):
        patient = self.create_patient(
            date_birth=date(1990, 1, 1),
            admission_date=date(2023, 1, 1),
            treatment_withdrawal_date=date(2023, 6, 1)
        )
        try:
            patient.save()
        except ValidationError:
            self.fail("Valid dates raised ValidationError.")

    def test_valid_dates_withdrawal_none(self):
        patient = self.create_patient(
            date_birth=date(1990, 1, 1),
            admission_date=date(2023, 1, 1),
            treatment_withdrawal_date=None
        )
        try:
            patient.save()
        except ValidationError:
            self.fail("Valid dates with withdrawal_date=None raised ValidationError.")

    def test_valid_dates_admission_and_withdrawal_none(self):
        patient = self.create_patient(
            date_birth=date(1990, 1, 1),
            admission_date=None,
            treatment_withdrawal_date=None
        )
        try:
            patient.save()
        except ValidationError:
            self.fail("Valid dates with admission_date=None and withdrawal_date=None raised ValidationError.")

    def test_invalid_admission_date_before_birth_date(self):
        patient = self.create_patient(
            date_birth=date(2000, 1, 1),
            admission_date=date(1999, 12, 31)
        )
        with self.assertRaises(ValidationError, msg="تاریخ تولد باید قبل از تاریخ پذیرش باشد."):
            patient.save()

    def test_invalid_withdrawal_date_before_admission_date(self):
        patient = self.create_patient(
            admission_date=date(2023, 1, 1),
            treatment_withdrawal_date=date(2022, 12, 31)
        )
        with self.assertRaises(ValidationError, msg="تاریخ پذیرش باید قبل از تاریخ خروج از درمان باشد."):
            patient.save()


from decimal import Decimal

class PrescriptionValidationTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            file_number='PRESCR001',
            first_name='Test',
            last_name='PatientForPrescription',
            national_code='1112223330',
            marital_status=Patient.MARITAL_STATUS_CHOICES[0][0],
            education=Patient.EDUCATION_CHOICES[0][0],
            treatment_type=Patient.TREATMENT_TYPE_CHOICES[0][0],
            usage_duration="2 years",
            date_birth=date(1980, 1, 1),
            admission_date=date(2022, 1, 1)
        )
        self.medication_type = MedicationType.objects.create(
            name="Methadone",
            unit="mg"
        )
        self.valid_prescription_data = {
            'patient': self.patient,
            'medication_type': self.medication_type,
            'daily_dose': Decimal('10.00'),
            'treatment_duration': 30, # days
            'start_date': date(2023, 1, 1),
            'end_date': date(2023, 1, 31),
            'total_prescribed': Decimal('300.00'), # 10.00 * 30
            'notes': 'Standard prescription'
        }

    def create_prescription(self, **kwargs):
        """Helper to create a Prescription instance with overridden data."""
        data = {**self.valid_prescription_data, **kwargs}
        # Ensure related objects are instances, not just PKs, if not already.
        if 'patient' not in kwargs: data['patient'] = self.patient
        if 'medication_type' not in kwargs: data['medication_type'] = self.medication_type
        return Prescription(**data)

    # Date Consistency Tests
    def test_valid_dates(self):
        prescription = self.create_prescription(
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31) # end_date is after start_date
        )
        try:
            prescription.save() # Should not raise ValidationError
        except ValidationError:
            self.fail("Valid prescription dates raised ValidationError.")

    def test_invalid_end_date_before_start_date(self):
        prescription = self.create_prescription(
            start_date=date(2023, 1, 15),
            end_date=date(2023, 1, 10)
        )
        with self.assertRaises(ValidationError, msg="تاریخ شروع باید قبل از تاریخ پایان باشد."):
            prescription.save()

    def test_invalid_start_date_equals_end_date(self):
        prescription = self.create_prescription(
            start_date=date(2023, 1, 15),
            end_date=date(2023, 1, 15)
        )
        with self.assertRaises(ValidationError, msg="تاریخ شروع باید قبل از تاریخ پایان باشد."):
            prescription.save()

    # Total Prescribed Consistency Tests
    def test_valid_total_prescribed(self):
        prescription = self.create_prescription(
            daily_dose=Decimal('20.00'),
            treatment_duration=10,
            total_prescribed=Decimal('200.00') # 20 * 10
        )
        try:
            prescription.save()
        except ValidationError:
            self.fail("Valid total_prescribed raised ValidationError.")

    def test_invalid_total_prescribed_too_high(self):
        prescription = self.create_prescription(
            daily_dose=Decimal('10.00'),
            treatment_duration=10,
            total_prescribed=Decimal('101.00') # Expected 100.00
        )
        expected_msg_part = "مقدار کل تجویز شده (101.00) با مقدار محاسبه شده (100.00) مغایرت دارد."
        with self.assertRaisesMessage(ValidationError, expected_msg_part):
            prescription.save()


from patients.models import DrugInventory # Already have Patient, MT, Prescription, ValidationE, date, Decimal

class MedicationDistributionValidationTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            file_number='DISTRO001', first_name='Distro', last_name='Patient',
            national_code='4445556660', marital_status='single',
            education='bachelor', treatment_type='detox', usage_duration="3m",
            date_birth=date(1995,1,1), admission_date=date(2023,1,1)
        )
        self.medication_type = MedicationType.objects.create(name="Buprenorphine", unit="mg")

        # Initial inventory: Set a reasonable stock for most tests
        self.inventory = DrugInventory.objects.create(
            medication_type=self.medication_type,
            current_stock=Decimal('200.00'), # Enough for several small distributions
            minimum_stock=Decimal('10.00')
        )

        self.prescription = Prescription.objects.create(
            patient=self.patient,
            medication_type=self.medication_type,
            daily_dose=Decimal('10.00'),
            treatment_duration=10, # total_prescribed will be 100
            total_prescribed=Decimal('100.00'),
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 10)
        )

        self.valid_distribution_data = {
            'prescription': self.prescription,
            'distribution_date': date(2023, 1, 2),
            'amount': Decimal('20.00'), # 2 daily doses
            'remaining': Decimal('0.00'), # Assuming this is calculated or not strictly validated here
            'notes': 'Initial valid distribution.'
        }

    def create_distribution(self, **kwargs):
        data = {**self.valid_distribution_data, **kwargs}
        if 'prescription' not in kwargs: data['prescription'] = self.prescription
        return MedicationDistribution(**data)

    # Amount vs. Total Prescribed Tests
    def test_valid_distribution_amount(self):
        distribution = self.create_distribution(amount=Decimal('50.00'))
        initial_stock = self.inventory.current_stock
        try:
            distribution.save()
            self.inventory.refresh_from_db() # Get updated stock
            self.assertEqual(self.inventory.current_stock, initial_stock - Decimal('50.00'))
        except ValidationError:
            self.fail("Valid distribution amount raised ValidationError.")

    def test_invalid_single_distribution_exceeds_total_prescribed(self):
        distribution = self.create_distribution(amount=Decimal('101.00')) # Prescription total is 100
        with self.assertRaisesMessage(ValidationError, "بیشتر از مقدار کل تجویز شده"):
            distribution.save()

    def test_invalid_cumulative_distribution_exceeds_total_prescribed(self):
        dist1 = self.create_distribution(amount=Decimal('60.00'), distribution_date=date(2023,1,1))
        dist1.save() # This one is valid and reduces stock

        self.inventory.refresh_from_db()

        dist2 = self.create_distribution(amount=Decimal('50.00'), distribution_date=date(2023,1,2)) # 60 + 50 = 110 > 100
        with self.assertRaisesMessage(ValidationError, "بیشتر از مقدار کل تجویز شده"):
            dist2.save()

    def test_update_distribution_exceeds_total_prescribed(self):
        distribution = self.create_distribution(amount=Decimal('10.00'))
        distribution.save() # Saves fine, stock reduced.

        # Now try to update it to an amount that makes cumulative exceed
        # First, let's make another small distribution to make the test more interesting
        dist2 = self.create_distribution(amount=Decimal('10.00'), distribution_date=date(2023,1,3))
        dist2.save() # Total distributed = 20. Remaining allowed = 80.

        distribution.amount = Decimal('90.00') # Try to update first from 10 to 90. 90 (new) + 10 (dist2) = 100. This should be fine.
        try:
            distribution.save() # This save is an update, inventory logic in save() is skipped for updates.
        except ValidationError:
            self.fail("Updating distribution to a valid cumulative amount failed.")

        distribution.amount = Decimal('91.00') # 91 (new) + 10 (dist2) = 101 > 100.
        with self.assertRaisesMessage(ValidationError, "بیشتر از مقدار کل تجویز شده"):
            distribution.save()


    # Distribution Date Tests
    def test_valid_distribution_date(self):
        distribution = self.create_distribution(distribution_date=date(2023, 1, 5)) # Prescription 1/1 to 1/10
        try:
            distribution.save()
        except ValidationError:
            self.fail("Valid distribution date raised ValidationError.")

    def test_invalid_distribution_date_before_prescription_start(self):
        distribution = self.create_distribution(distribution_date=date(2022, 12, 31))
        with self.assertRaisesMessage(ValidationError, "تاریخ توزیع نمی‌تواند قبل از تاریخ شروع نسخه باشد."):
            distribution.save()

    def test_invalid_distribution_date_after_prescription_end(self):
        distribution = self.create_distribution(distribution_date=date(2023, 1, 11))
        with self.assertRaisesMessage(ValidationError, "تاریخ توزیع نمی‌تواند بعد از تاریخ پایان نسخه باشد."):
            distribution.save()

    # Inventory Checks
    def test_distribution_sufficient_inventory(self):
        self.inventory.current_stock = Decimal('50.00')
        self.inventory.save()
        distribution = self.create_distribution(amount=Decimal('30.00'))
        initial_stock = self.inventory.current_stock
        try:
            distribution.save()
            self.inventory.refresh_from_db()
            self.assertEqual(self.inventory.current_stock, initial_stock - Decimal('30.00'))
        except ValidationError:
            self.fail("Distribution with sufficient inventory raised ValidationError.")

    def test_distribution_insufficient_inventory(self):
        self.inventory.current_stock = Decimal('10.00')
        self.inventory.save()
        distribution = self.create_distribution(amount=Decimal('20.00'))
        # The error message comes from the model's save method (MedicationDistribution)
        with self.assertRaisesMessage(ValidationError, "موجودی کافی برای این دارو در انبار نیست."):
            distribution.save()

    def test_distribution_no_inventory_record(self):
        self.inventory.delete() # Remove the inventory record
        distribution = self.create_distribution(amount=Decimal('10.00'))
        with self.assertRaisesMessage(ValidationError, "موجودی برای این دارو تعریف نشده است."):
            distribution.save()

    def test_update_distribution_does_not_recheck_inventory(self):
        self.inventory.current_stock = Decimal('30.00')
        self.inventory.save()

        distribution = self.create_distribution(amount=Decimal('20.00'))
        distribution.save() # Saves, stock becomes 10.00

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.current_stock, Decimal('10.00'))


from io import StringIO
from django.core.management import call_command

class ManagementCommandTests(TestCase):
    def setUp(self):
        # Common patient for prescription/distribution tests
        self.patient = Patient.objects.create(
            file_number='CMDTEST01', first_name='Cmd', last_name='Patient',
            national_code='0010020030', marital_status='married',
            education='master', treatment_type='maintenance', usage_duration="1y",
            date_birth=date(1985, 5, 5), admission_date=date(2022, 3, 3)
        )
        self.med_type = MedicationType.objects.create(name="Methadone Syrup", unit="ml")
        self.inventory = DrugInventory.objects.create(medication_type=self.med_type, current_stock=Decimal('1000.00'))

        self.prescription = Prescription.objects.create(
            patient=self.patient, medication_type=self.med_type,
            daily_dose=Decimal('50'), treatment_duration=10, total_prescribed=Decimal('500'), # 50 * 10
            start_date=date(2023, 1, 1), end_date=date(2023, 1, 10)
        )

    def test_scan_patients_command(self):
        # Valid patient (already created in general setUp if needed, or create one here)
        Patient.objects.create(
            file_number='VALIDP01', first_name='Valid', last_name='Patient',
            national_code='1234567890', phone_number='09112223344',
            marital_status='single', education='high_school', treatment_type='detox', usage_duration="6m",
            date_birth=date(1990,1,1), admission_date=date(2023,1,1)
        )

        p_invalid_nc = Patient.objects.create(
            file_number='INVNC01', first_name='NC', last_name='Error', national_code='123', # Invalid NC
            marital_status='single', education='high_school', treatment_type='detox', usage_duration="6m",
            date_birth=date(1990,1,1), admission_date=date(2023,1,1)
        )
        p_invalid_phone = Patient.objects.create(
            file_number='INVPH01', first_name='Phone', last_name='Error', national_code='1122334455',
            phone_number='0912', # Invalid Phone
            marital_status='single', education='high_school', treatment_type='detox', usage_duration="6m",
            date_birth=date(1990,1,1), admission_date=date(2023,1,1)
        )
        p_invalid_date = Patient.objects.create(
            file_number='INVDT01', first_name='Date', last_name='Error', national_code='6677889900',
            marital_status='single', education='high_school', treatment_type='detox', usage_duration="6m",
            date_birth=date(2023, 2, 1), admission_date=date(2023, 1, 1) # Admission < Birth
        )

        out = StringIO()
        # Count self.patient as well for total scanned
        total_patients_including_cmdtest01 = Patient.objects.count() # Should be 5 if self.patient is unique

        call_command('scan_patients', stdout=out)
        output = out.getvalue()

        self.assertIn(f"ERROR: Patient file_number {p_invalid_nc.file_number}", output)
        self.assertIn("کد ملی باید دقیقا ۱۰ رقم باشد.", output)
        self.assertIn(f"ERROR: Patient file_number {p_invalid_phone.file_number}", output)
        self.assertIn("شماره تلفن باید ۱۱ رقم باشد.", output)
        self.assertIn(f"ERROR: Patient file_number {p_invalid_date.file_number}", output)
        self.assertIn("تاریخ تولد باید قبل از تاریخ پذیرش باشد.", output)

        self.assertIn(f"Scan complete. {total_patients_including_cmdtest01} patients scanned, 3 errors found.", output)

    def test_scan_prescriptions_command(self):
        # Valid prescription already in self.prescription

        pr_invalid_date = Prescription.objects.create(
            patient=self.patient, medication_type=self.med_type,
            daily_dose=Decimal('20'), treatment_duration=5, total_prescribed=Decimal('100'),
            start_date=date(2023, 2, 10), end_date=date(2023, 2, 1) # End < Start
        )
        pr_invalid_total = Prescription.objects.create(
            patient=self.patient, medication_type=self.med_type,
            daily_dose=Decimal('30'), treatment_duration=10, total_prescribed=Decimal('301'), # Expected 300
            start_date=date(2023, 3, 1), end_date=date(2023, 3, 10)
        )

        out = StringIO()
        total_prescriptions = Prescription.objects.count() # Should be 3

        call_command('scan_prescriptions', stdout=out)
        output = out.getvalue()

        self.assertIn(f"ERROR: Prescription ID {pr_invalid_date.id}:", output)
        self.assertIn("تاریخ شروع باید قبل از تاریخ پایان باشد.", output)
        self.assertIn(f"ERROR: Prescription ID {pr_invalid_total.id}:", output)
        self.assertIn("مقدار کل تجویز شده (301) با مقدار محاسبه شده (300) مغایرت دارد.", output)

        self.assertIn(f"Scan complete. {total_prescriptions} prescriptions scanned, 2 errors found.", output)

    def test_scan_medication_distributions_command(self):
        # Valid distribution
        MedicationDistribution.objects.create(
            prescription=self.prescription, distribution_date=date(2023,1,2), amount=Decimal('50')
        )

        # Invalid: Amount > total_prescribed for the prescription (total_prescribed is 500)
        # We need a new prescription for this or ensure this is the only distribution to clearly exceed
        prescription_for_big_dist = Prescription.objects.create(
            patient=self.patient, medication_type=self.med_type,
            daily_dose=Decimal('10'), treatment_duration=5, total_prescribed=Decimal('50'), # Max 50
            start_date=date(2023, 2, 1), end_date=date(2023, 2, 5)
        )
        md_invalid_amount = MedicationDistribution.objects.create(
            prescription=prescription_for_big_dist, distribution_date=date(2023,2,1),
            amount=Decimal('60') # Exceeds 50
        )

        # Invalid: Distribution date outside prescription period
        md_invalid_date = MedicationDistribution.objects.create(
            prescription=self.prescription, distribution_date=date(2023, 1, 15), # Prescription ends 2023,1,10
            amount=Decimal('20')
        )

        out = StringIO()
        total_distributions = MedicationDistribution.objects.count() # Should be 3

        # Lower inventory to test inventory check for a new valid distribution if scan command included it
        # However, scan commands typically don't create/save, just read.
        # The inventory checks in MedicationDistribution's save() are for actual saves, not scans.
        # The scan command re-implements checks, but not inventory side-effects.

        call_command('scan_medication_distributions', stdout=out)
        output = out.getvalue()

        self.assertIn(f"ERROR: MedicationDistribution ID {md_invalid_amount.id}:", output)
        # The error message for amount check in scan command is slightly different from model's save
        # It checks total_amount_distributed_for_prescription > prescription.total_prescribed
        self.assertIn(f"مجموع مقادیر توزیع شده برای نسخه ID {prescription_for_big_dist.id} ({md_invalid_amount.amount}) بیشتر از مقدار کل تجویز شده ({prescription_for_big_dist.total_prescribed}) است.", output)

        self.assertIn(f"ERROR: MedicationDistribution ID {md_invalid_date.id}:", output)
        self.assertIn(f"تاریخ توزیع ({md_invalid_date.distribution_date.strftime('%Y-%m-%d') if isinstance(md_invalid_date.distribution_date, date) else md_invalid_date.distribution_date}) نمی‌تواند بعد از تاریخ پایان نسخه ({self.prescription.end_date.strftime('%Y-%m-%d') if isinstance(self.prescription.end_date, date) else self.prescription.end_date}) باشد", output)

        self.assertIn(f"Scan complete. {total_distributions} distributions scanned, 2 errors found.", output)

        # Try to update the distribution. Current save logic skips inventory check for updates.
        distribution.notes = "Updated notes."
        distribution.amount = Decimal('25.00') # This would fail if it were a new distribution with stock at 10.
                                            # And it also makes cumulative amount 25, which is fine for total_prescribed=100

        try:
            distribution.save() # Should save without inventory error.
        except ValidationError as e:
            if "موجودی" in str(e): # Check if the error is inventory related
                 self.fail("Updating distribution unexpectedly failed due to inventory check.")
            # Any other validation error is also a fail for this specific test's intent
            self.fail(f"Updating distribution failed with unexpected ValidationError: {e}")

        # Stock should remain unchanged because inventory logic is skipped for updates
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.current_stock, Decimal('10.00'))

    def test_invalid_total_prescribed_too_low(self):
        prescription = self.create_prescription(
            daily_dose=Decimal('10.00'),
            treatment_duration=10,
            total_prescribed=Decimal('99.00') # Expected 100.00
        )
        expected_msg_part = "مقدار کل تجویز شده (99.00) با مقدار محاسبه شده (100.00) مغایرت دارد."
        with self.assertRaisesMessage(ValidationError, expected_msg_part):
            prescription.save()

    def test_valid_total_prescribed_zero_dose(self):
        prescription = self.create_prescription(
            daily_dose=Decimal('0.00'),
            treatment_duration=30,
            total_prescribed=Decimal('0.00')
        )
        try:
            prescription.save()
        except ValidationError:
            self.fail("Valid total_prescribed with zero dose raised ValidationError.")

    def test_valid_total_prescribed_zero_duration(self):
        prescription = self.create_prescription(
            daily_dose=Decimal('50.00'),
            treatment_duration=0,
            total_prescribed=Decimal('0.00')
        )
        try:
            prescription.save()
        except ValidationError:
            self.fail("Valid total_prescribed with zero duration raised ValidationError.")

    def test_total_prescribed_recalculation(self):
        # Test if total_prescribed is correctly calculated if not provided (though our save method validates, not calculates)
        # This test actually verifies that if total_prescribed is wrong, it errors.
        prescription = self.create_prescription(
            daily_dose=Decimal('15.00'),
            treatment_duration=10
            # total_prescribed is self.valid_prescription_data['total_prescribed'] = 300.00 by default
            # which is not 15.00 * 10 = 150.00
        )
        expected_msg_part = f"مقدار کل تجویز شده ({self.valid_prescription_data['total_prescribed']}) با مقدار محاسبه شده (150.00) مغایرت دارد."
        with self.assertRaisesMessage(ValidationError, expected_msg_part):
            prescription.save()

    def test_birth_date_equals_admission_date(self):
        patient = self.create_patient(
            date_birth=date(2000,1,1),
            admission_date=date(2000,1,1)
        )
        with self.assertRaises(ValidationError, msg="تاریخ تولد باید قبل از تاریخ پذیرش باشد."):
            patient.save()

    def test_admission_date_equals_withdrawal_date(self):
        patient = self.create_patient(
            admission_date=date(2023,1,1),
            treatment_withdrawal_date=date(2023,1,1)
        )
        with self.assertRaises(ValidationError, msg="تاریخ پذیرش باید قبل از تاریخ خروج از درمان باشد."):
            patient.save()
