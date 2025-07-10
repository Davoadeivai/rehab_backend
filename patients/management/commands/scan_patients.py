import argparse
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from patients.models import Patient # Assuming your Patient model is in patients.models

class Command(BaseCommand):
    help = 'Scans all patient records for data validation issues based on custom logic in Patient.save().'

    def handle(self, *args, **options):
        self.stdout.write("Starting patient data scan...")

        patients_scanned = 0
        errors_found = 0

        for patient in Patient.objects.all():
            patients_scanned += 1
            error_messages = []

            # 1. National code validation
            if patient.national_code:
                if not patient.national_code.isdigit():
                    error_messages.append("کد ملی باید فقط شامل اعداد باشد.")
                if len(patient.national_code) != 10:
                    error_messages.append("کد ملی باید دقیقا ۱۰ رقم باشد.")
            else:
                # Assuming national_code is mandatory, though model doesn't strictly enforce it with blank=False
                # For this scan, we'll flag if it's missing, aligning with typical requirements.
                error_messages.append("کد ملی وارد نشده است.")

            # 2. Phone number validation
            if patient.phone_number:
                if not patient.phone_number.isdigit():
                    error_messages.append("شماره تلفن باید فقط شامل اعداد باشد.")
                if len(patient.phone_number) != 11:
                    error_messages.append("شماره تلفن باید ۱۱ رقم باشد.")
            # else:
                # Phone number can be blank/null based on model (null=True, blank=True)
                # So, no error if it's missing.

            # 3. Date consistency checks
            if patient.date_birth and patient.admission_date:
                if patient.date_birth >= patient.admission_date:
                    error_messages.append("تاریخ تولد باید قبل از تاریخ پذیرش باشد.")

            if patient.admission_date and patient.treatment_withdrawal_date:
                if patient.admission_date >= patient.treatment_withdrawal_date:
                    error_messages.append("تاریخ پذیرش باید قبل از تاریخ خروج از درمان باشد.")

            if error_messages:
                errors_found += 1
                self.stdout.write(self.style.ERROR(f"ERROR: Patient file_number {patient.file_number} (PK: {patient.pk}):"))
                for msg in error_messages:
                    self.stdout.write(self.style.ERROR(f"  - {msg}"))
            # else:
            #    self.stdout.write(self.style.SUCCESS(f"Patient PK {patient.pk} is valid."))

        self.stdout.write(self.style.SUCCESS(f"\nScan complete. {patients_scanned} patients scanned, {errors_found} errors found."))
