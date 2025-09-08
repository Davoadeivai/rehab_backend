from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from patients.models import MedicationDistribution, Prescription, DrugInventory # DrugInventory might not be directly needed but good to be aware of related models
from django.db.models import Sum
from decimal import Decimal

class Command(BaseCommand):
    help = 'Scans all medication distribution records for data validation issues.'

    def handle(self, *args, **options):
        self.stdout.write("Starting medication distribution data scan...")

        distributions_scanned = 0
        errors_found = 0

        # Optimization: Cache prescription validation results to avoid redundant checks for the same prescription
        # However, the request is to validate per distribution, so we'll stick to that for now.
        # If performance becomes an issue on large datasets, we could group by prescription first.

        for dist in MedicationDistribution.objects.select_related('prescription').all():
            distributions_scanned += 1
            error_messages = []

            prescription = dist.prescription
            if not prescription:
                # This should not happen if database foreign key constraints are active
                error_messages.append(f"توزیع به نسخه معتبری متصل نیست.")
                errors_found += 1
                self.stdout.write(self.style.ERROR(f"ERROR: MedicationDistribution ID {dist.id}:"))
                for msg in error_messages:
                    self.stdout.write(self.style.ERROR(f"  - {msg}"))
                continue # Skip further checks for this distribution

            # 1. Distribution Date within Prescription Period
            if dist.distribution_date and prescription.start_date:
                if dist.distribution_date < prescription.start_date:
                    error_messages.append(
                        f"تاریخ توزیع ({dist.distribution_date}) نمی‌تواند قبل از تاریخ شروع نسخه ({prescription.start_date}) باشد (نسخه ID: {prescription.id})."
                    )
            else:
                if not dist.distribution_date:
                     error_messages.append("تاریخ توزیع وارد نشده است.")
                if not prescription.start_date:
                     error_messages.append(f"تاریخ شروع برای نسخه ID: {prescription.id} وارد نشده است.")


            if dist.distribution_date and prescription.end_date:
                if dist.distribution_date > prescription.end_date:
                    error_messages.append(
                        f"تاریخ توزیع ({dist.distribution_date}) نمی‌تواند بعد از تاریخ پایان نسخه ({prescription.end_date}) باشد (نسخه ID: {prescription.id})."
                    )
            else:
                if not dist.distribution_date:
                    # Already handled above, but good to be thorough if logic changes
                    pass
                if not prescription.end_date:
                     error_messages.append(f"تاریخ پایان برای نسخه ID: {prescription.id} وارد نشده است.")


            # 2. Amount vs. Total Prescribed (Cumulative for the prescription)
            # For each distribution, we check the state of its parent prescription's total distributions
            # This means if a prescription is over-distributed, each of its distributions will be flagged.
            # This is acceptable for a scan.

            # Get all distributions for this specific prescription
            all_distributions_for_prescription = MedicationDistribution.objects.filter(prescription=prescription)
            # Sum their amounts
            total_amount_distributed_for_prescription = all_distributions_for_prescription.aggregate(total=Sum('amount'))['total'] or Decimal('0')

            if prescription.total_prescribed is not None:
                if total_amount_distributed_for_prescription > prescription.total_prescribed:
                    error_messages.append(
                        f"مجموع مقادیر توزیع شده برای نسخه ID {prescription.id} ({total_amount_distributed_for_prescription}) "
                        f"بیشتر از مقدار کل تجویز شده ({prescription.total_prescribed}) است."
                    )
            else:
                error_messages.append(f"مقدار کل تجویز شده برای نسخه ID: {prescription.id} وارد نشده است.")


            if error_messages:
                errors_found += 1
                # Check if header already printed for this distribution
                # (Could happen if prescription was null)
                if not (prescription is None and distributions_scanned > 0 and errors_found == distributions_scanned ): # simple check
                     self.stdout.write(self.style.ERROR(f"ERROR: MedicationDistribution ID {dist.id}:"))
                for msg in error_messages:
                    self.stdout.write(self.style.ERROR(f"  - {msg}"))
            # else:
            #    self.stdout.write(self.style.SUCCESS(f"MedicationDistribution ID {dist.id} is valid."))

        self.stdout.write(self.style.SUCCESS(f"\nScan complete. {distributions_scanned} distributions scanned, {errors_found} errors found."))
