# patients/services/medication_summary.py

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from patients.models import MedicationType, MedicationDistribution

def monthly_medication_summary():
    return MedicationDistribution.objects.annotate(
        month=TruncMonth('distribution_date')
    ).values('prescription__medication_type__name', 'month').annotate(
        total_amount=Sum('amount')
    ).order_by('prescription__medication_type__name', 'month')
