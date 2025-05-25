# patients/services/medication_summary.py

from django.db.models import Sum
from django.db.models.functions import TruncMonth
# from patients.models import Medication

def monthly_medication_summary():
    return Medication.objects.annotate(
        month=TruncMonth('prescription_date')
    ).values('نام_دارو', 'month').annotate(
        total_cost=Sum('prescription_cost')
    ).order_by('نام_دارو', 'month')
