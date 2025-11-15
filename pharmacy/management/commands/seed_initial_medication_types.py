from django.core.management.base import BaseCommand

from patients.medication_models import MedicationType
from pharmacy.models import INITIAL_DRUGS, InventoryLog


class Command(BaseCommand):
    help = "ایجاد رکوردهای MedicationType بر اساس INITIAL_DRUGS و سپس سینک آن‌ها با داروخانه"

    def handle(self, *args, **options):
        created_count = 0
        for drug_data in INITIAL_DRUGS:
            name = drug_data["name"]
            # فرض می‌کنیم همه این داروها واحد "قرص" یا "شربت" دارند؛
            # اگر از قبل MedicationType با همین نام وجود داشته باشد، دوباره ساخته نمی‌شود.
            obj, created = MedicationType.objects.get_or_create(
                name=name,
                defaults={
                    "description": drug_data.get("description", ""),
                    "unit": drug_data.get("category", "واحد"),
                },
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"MedicationType '{obj.name}' ایجاد شد."))
            else:
                self.stdout.write(self.style.WARNING(f"MedicationType '{obj.name}' قبلاً وجود دارد."))

        # بعد از ساخت/تکمیل MedicationType ها، داروخانه را با آن‌ها سینک می‌کنیم
        InventoryLog.sync_medication_types_to_drugs()
        self.stdout.write(
            self.style.SUCCESS(
                f"ایجاد/تکمیل {created_count} MedicationType جدید و سینک داروخانه با موفقیت انجام شد."
            )
        )
