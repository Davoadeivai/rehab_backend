# patients/utils.py
from datetime import timedelta
from django.utils import timezone
from .models import Medication

def calculate_medication_usage(patient_id, days):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    return Medication.objects.filter(
        patient_id=patient_id,
        prescription_date__range=(start_date, end_date)
    ).aggregate(total_cost=models.Sum('prescription_cost'))
