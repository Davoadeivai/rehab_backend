from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from patients.models import Prescription # Assuming Prescription model is in patients.models
import decimal # For precise arithmetic with DecimalFields

class Command(BaseCommand):
    help = 'Scans all prescription records for data validation issues based on custom logic in Prescription.save().'

    def handle(self, *args, **options):
        self.stdout.write("Starting prescription data scan...")

        prescriptions_scanned = 0
        errors_found = 0

        for prescription in Prescription.objects.all():
            prescriptions_scanned += 1
            error_messages = []

            # 1. Date consistency check
            if prescription.start_date and prescription.end_date:
                if prescription.start_date >= prescription.end_date:
                    error_messages.append("تاریخ شروع باید قبل از تاریخ پایان باشد.")
            elif not prescription.start_date:
                error_messages.append("تاریخ شروع وارد نشده است.") # Assuming start_date is mandatory
            elif not prescription.end_date:
                error_messages.append("تاریخ پایان وارد نشده است.") # Assuming end_date is mandatory


            # 2. total_prescribed validation
            # Fields daily_dose and treatment_duration are non-nullable DecimalField and IntegerField respectively.
            # total_prescribed is a non-nullable DecimalField.
            if prescription.daily_dose is not None and prescription.treatment_duration is not None:
                try:
                    # Ensure treatment_duration is treated as a Decimal for multiplication if necessary,
                    # or ensure daily_dose is compatible with integer multiplication.
                    # Python's Decimal * int works fine.
                    expected_total_prescribed = prescription.daily_dose * decimal.Decimal(prescription.treatment_duration)
                    if prescription.total_prescribed != expected_total_prescribed:
                        error_messages.append(
                            f"مقدار کل تجویز شده ({prescription.total_prescribed}) با مقدار محاسبه شده "
                            f"({expected_total_prescribed} = {prescription.daily_dose} * {prescription.treatment_duration}) مغایرت دارد."
                        )
                except TypeError: # Should not happen with model constraints but good for safety
                    error_messages.append("خطا در محاسبه مقدار کل تجویز شده به دلیل نوع داده نامعتبر برای دوز روزانه یا مدت درمان.")
            else:
                # This case implies one of daily_dose or treatment_duration is None, which model constraints should prevent.
                # If total_prescribed is also None, it might be a partially created record.
                # If total_prescribed is set, it's an inconsistency.
                 error_messages.append("دوز روزانه یا مدت درمان برای بررسی مقدار کل تجویز شده وارد نشده است.")

            if error_messages:
                errors_found += 1
                self.stdout.write(self.style.ERROR(f"ERROR: Prescription ID {prescription.id}:"))
                for msg in error_messages:
                    self.stdout.write(self.style.ERROR(f"  - {msg}"))
            # else:
            #    self.stdout.write(self.style.SUCCESS(f"Prescription ID {prescription.id} is valid."))

        self.stdout.write(self.style.SUCCESS(f"\nScan complete. {prescriptions_scanned} prescriptions scanned, {errors_found} errors found."))
