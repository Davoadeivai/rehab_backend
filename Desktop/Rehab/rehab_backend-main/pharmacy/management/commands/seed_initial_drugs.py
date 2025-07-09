from django.core.management.base import BaseCommand
from pharmacy.models import Drug, INITIAL_DRUGS

class Command(BaseCommand):
    help = 'افزودن داروهای اولیه فارسی به داروخانه'

    def handle(self, *args, **options):
        for drug_data in INITIAL_DRUGS:
            obj, created = Drug.objects.get_or_create(name=drug_data['name'], defaults=drug_data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"داروی '{obj.name}' اضافه شد."))
            else:
                self.stdout.write(self.style.WARNING(f"داروی '{obj.name}' قبلاً وجود دارد.")) 