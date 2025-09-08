from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Patient
from .medication_models import Medication, DrugQuota, DrugInventory, MedicationType
from django.core.management import call_command
from io import StringIO
import json
from django.utils import timezone

User = get_user_model()

class ManagementCommandTests(TestCase):
    def setUp(self):
        # ایجاد کاربر برای تست
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        
        # ایجاد بیمار برای تست
        self.patient = Patient.objects.create(
            file_number='CMDTEST01',
            first_name='دستور',
            last_name='تست',
            national_code='0010020030',
            gender='M',
            marital_status='married',
            education='master',
            treatment_type='MMT',
            usage_duration="1y",
            date_birth='1365-05-05',
            admission_date='1401-03-03',
            status='active'
        )
        
        # ایجاد نوع دارو
        self.med_type = MedicationType.objects.create(
            name='شربت متادون',
            unit='میلی‌لیتر',
            description='داروی ترک اعتیاد',
            is_active=True
        )
        
        # ایجاد موجودی انبار
        self.inventory = DrugInventory.objects.create(
            medication_type=self.med_type,
            current_stock=1000.0,
            minimum_stock=100.0,
            last_updated='1402-01-01'
        )
        
        # ایجاد نسخه
        self.prescription = Prescription.objects.create(
            patient=self.patient,
            medication_type=self.med_type,
            daily_dose=50.0,
            treatment_duration=10,
            total_prescribed=500.0,  # 50 * 10
            start_date='1402-01-01',
            end_date='1402-01-10',
            status='active',
            prescribed_by=self.user
        )
        
        # ایجاد سهمیه دارو
        self.drug_quota = DrugQuota.objects.create(
            patient=self.patient,
            medication_type=self.med_type,
            monthly_quota=1000.0,
            remaining_quota=1000.0,
            start_date='1402-01-01',
            end_date='1402-12-29'
        )

    def test_scan_patients_command(self):
        """تست دستور اسکن بیماران"""
        # ایجاد بیماران معتبر و نامعتبر
        valid_patient = Patient.objects.create(
            file_number='VALIDP01',
            first_name='معتبر',
            last_name='بیمار',
            national_code='1234567890',
            phone_number='09123456789',
            gender='M',
            marital_status='single',
            education='high_school',
            treatment_type='MMT',
            usage_duration="6m",
            date_birth='1370-01-01',
            admission_date='1402-01-01',
            status='active'
        )
        
        invalid_nc = Patient.objects.create(
            file_number='INVNC01',
            first_name='کدملی',
            last_name='نامعتبر',
            national_code='123',  # کد ملی نامعتبر
            gender='M',
            marital_status='single',
            education='high_school',
            treatment_type='MMT',
            usage_duration="6m",
            date_birth='1370-01-01',
            admission_date='1402-01-01',
            status='active'
        )
        
        invalid_phone = Patient.objects.create(
            file_number='INVPH01',
            first_name='تلفن',
            last_name='نامعتبر',
            national_code='1122334455',
            phone_number='0912',  # شماره تلفن نامعتبر
            gender='M',
            marital_status='single',
            education='high_school',
            treatment_type='MMT',
            usage_duration="6m",
            date_birth='1370-01-01',
            admission_date='1402-01-01',
            status='active'
        )
        
        invalid_date = Patient.objects.create(
            file_number='INVDT01',
            first_name='تاریخ',
            last_name='نامعتبر',
            national_code='6677889900',
            gender='M',
            marital_status='single',
            education='high_school',
            treatment_type='MMT',
            usage_duration="6m",
            date_birth='1402-01-01',  # تاریخ تولد بعد از تاریخ پذیرش
            admission_date='1401-01-01',
            status='active'
        )
        
        out = StringIO()
        total_patients = Patient.objects.count()  # تعداد کل بیماران شامل موارد نامعتبر
        
        call_command('scan_patients', stdout=out)
        output = out.getvalue()
        
        # بررسی خروجی دستور
        self.assertIn(f"ERROR: Patient file_number {invalid_nc.file_number}", output)
        self.assertIn("کد ملی باید دقیقا ۱۰ رقم باشد.", output)
        self.assertIn(f"ERROR: Patient file_number {invalid_phone.file_number}", output)
        self.assertIn("شماره تلفن باید ۱۱ رقم باشد.", output)
        self.assertIn(f"ERROR: Patient file_number {invalid_date.file_number}", output)
        self.assertIn("تاریخ تولد باید قبل از تاریخ پذیرش باشد.", output)
        self.assertIn(f"Scan complete. {total_patients} patients scanned, 3 errors found.", output)
    
    def test_scan_prescriptions_command(self):
        """تست دستور اسکن نسخه‌ها"""
        # ایجاد نسخه‌های معتبر و نامعتبر
        valid_prescription = Prescription.objects.create(
            patient=self.patient,
            medication_type=self.med_type,
            daily_dose=20.0,
            treatment_duration=10,
            total_prescribed=200.0,  # 20 * 10
            start_date='1402-02-01',
            end_date='1402-02-10',
            status='active',
            prescribed_by=self.user
        )
        
        invalid_date = Prescription.objects.create(
            patient=self.patient,
            medication_type=self.med_type,
            daily_dose=20.0,
            treatment_duration=10,
            total_prescribed=200.0,
            start_date='1402-02-10',  # تاریخ شروع بعد از تاریخ پایان
            end_date='1402-02-01',
            status='active',
            prescribed_by=self.user
        )
        
        invalid_total = Prescription.objects.create(
            patient=self.patient,
            medication_type=self.med_type,
            daily_dose=30.0,
            treatment_duration=10,
            total_prescribed=301.0,  # باید 300 باشد (30 * 10)
            start_date='1402-03-01',
            end_date='1402-03-10',
            status='active',
            prescribed_by=self.user
        )
        
        out = StringIO()
        total_prescriptions = Prescription.objects.count()
        
        call_command('scan_prescriptions', stdout=out)
        output = out.getvalue()
        
        # بررسی خروجی دستور
        self.assertIn(f"ERROR: Prescription ID {invalid_date.id}:", output)
        self.assertIn("تاریخ شروع باید قبل از تاریخ پایان باشد.", output)
        self.assertIn(f"ERROR: Prescription ID {invalid_total.id}:", output)
        self.assertIn("مقدار کل تجویز شده با حاصل ضرب دوز روزانه در مدت درمان مطابقت ندارد.", output)
        self.assertIn(f"Scan complete. {total_prescriptions} prescriptions scanned, 2 errors found.", output)
    
    def test_scan_medication_distributions_command(self):
        """تست دستور اسکن توزیع داروها"""
        # ایجاد توزیع‌های معتبر و نامعتبر
        valid_distribution = MedicationDistribution.objects.create(
            prescription=self.prescription,
            distribution_date='1402-01-05',
            amount=50.0,
            distributed_by=self.user,
            notes='توزیع معتبر تستی'
        )
        
        # توزیع با مقدار بیشتر از موجودی انبار
        invalid_inventory = MedicationDistribution(
            prescription=self.prescription,
            distribution_date='1402-01-06',
            amount=2000.0,  # بیشتر از موجودی انبار
            distributed_by=self.user,
            notes='توزیع با موجودی ناکافی'
        )
        
        # توزیع با تاریخ خارج از محدوده نسخه
        invalid_date = MedicationDistribution(
            prescription=self.prescription,
            distribution_date='1401-12-31',  # قبل از تاریخ شروع نسخه
            amount=50.0,
            distributed_by=self.user,
            notes='توزیع با تاریخ نامعتبر'
        )
        
        out = StringIO()
        
        # ابتدا توزیع‌های نامعتبر را ذخیره می‌کنیم تا خطاها را بگیریم
        try:
            invalid_inventory.save()
        except ValidationError:
            pass
            
        try:
            invalid_date.save()
        except ValidationError:
            pass
        
        # حالا دستور اسکن را اجرا می‌کنیم
        call_command('scan_medication_distributions', stdout=out)
        output = out.getvalue()
        
        # بررسی خروجی دستور
        self.assertIn("Scanning all medication distributions for validation issues...", output)
        self.assertIn("Scan complete.", output)
    
    def test_generate_monthly_reports_command(self):
        """تست دستور تولید گزارشات ماهانه"""
        # ایجاد داده‌های تستی برای گزارش
        from django.utils import timezone
        from datetime import timedelta
        
        # ایجاد توزیع‌های تستی
        today = timezone.now().date()
        last_month = today - timedelta(days=30)
        
        # توزیع در ماه جاری
        current_month_dist = MedicationDistribution.objects.create(
            prescription=self.prescription,
            distribution_date=today,
            amount=50.0,
            distributed_by=self.user,
            notes='توزیع ماه جاری'
        )
        
        # توزیع در ماه قبل
        last_month_dist = MedicationDistribution.objects.create(
            prescription=self.prescription,
            distribution_date=last_month,
            amount=30.0,
            distributed_by=self.user,
            notes='توزیع ماه قبل'
        )
        
        out = StringIO()
        call_command('generate_monthly_reports', '--month', today.month, '--year', today.year, stdout=out)
        output = out.getvalue()
        
        # بررسی خروجی دستور
        self.assertIn("گزارش ماهانه با موفقیت تولید شد", output)
        self.assertIn("تعداد توزیع‌ها: 1", output)
        self.assertIn("کل مقدار توزیع شده: 50.0", output)
    
    def test_update_drug_inventory_command(self):
        """تست دستور به‌روزرسانی موجودی انبار"""
        # ذخیره موجودی اولیه
        initial_stock = self.inventory.current_stock
        
        out = StringIO()
        call_command('update_drug_inventory', str(self.med_type.id), '100', '--add', stdout=out)
        output = out.getvalue()
        
        # بررسی به‌روزرسانی موجودی
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.current_stock, initial_stock + 100)
        self.assertIn("موجودی انبار با موفقیت به‌روزرسانی شد", output)
        self.assertIn(f"موجودی جدید: {self.inventory.current_stock}", output)
    
    def test_check_low_stock_command(self):
        """تست دستور بررسی موجودی کم"""
        # تنظیم موجودی به زیر حداقل
        self.inventory.current_stock = 50.0
        self.inventory.save()
        
        out = StringIO()
        call_command('check_low_stock', stdout=out)
        output = out.getvalue()
        
        # بررسی اخطار موجودی کم
        self.assertIn("هشدار: موجودی کم", output)
        self.assertIn(self.medication_type.name, output)
        self.assertIn("موجودی فعلی: 50.0", output)
        self.assertIn("حداقل موجودی: 100.0", output)
