from django.core.management.base import BaseCommand

from pharmacy.models import InventoryLog


class Command(BaseCommand):
    help = "سینک لیست داروهای بخش نسخه‌نویسی (MedicationType) با لیست داروخانه (Drug)"

    def handle(self, *args, **options):
        InventoryLog.sync_medication_types_to_drugs()
        self.stdout.write(self.style.SUCCESS("سینک داروهای نسخه‌نویسی با داروخانه با موفقیت انجام شد."))
