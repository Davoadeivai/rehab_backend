# -*- coding: utf-8 -*-
import sys
from django.core.management.base import BaseCommand
from django.utils import timezone
from ...alerts import check_all_alerts

# Set default encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    import codecs
    import locale
    import sys
    
    # Set stdout to use UTF-8
    if sys.version_info >= (3, 7):
        sys.stdout.reconfigure(encoding='utf-8')
    else:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    
    # Set locale to handle Persian characters
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'English_United States.1256')
        except locale.Error:
            pass

class Command(BaseCommand):
    help = 'Check and create system alerts'

    def handle(self, *args, **options):
        self.stdout.write('Checking system alerts...')
        start_time = timezone.now()
        
        try:
            check_all_alerts()
            
            end_time = timezone.now()
            duration = (end_time - start_time).total_seconds()
            
            self.stdout.write(
                self.style.SUCCESS(f'Alerts checked successfully. Execution time: {duration:.2f} seconds')
            )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Error checking alerts: {str(e)}')
            )
