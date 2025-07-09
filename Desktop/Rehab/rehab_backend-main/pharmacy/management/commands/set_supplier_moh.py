from django.core.management.base import BaseCommand
from pharmacy.models import Drug, Supplier

class Command(BaseCommand):
    help = 'Set all drugs supplier to وزارت بهداشت'

    def handle(self, *args, **options):
        supplier, created = Supplier.objects.get_or_create(name='وزارت بهداشت')
        Drug.objects.update(supplier=supplier)
        self.stdout.write(self.style.SUCCESS(f'All drugs supplier set to وزارت بهداشت (id={supplier.id})')) 