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
