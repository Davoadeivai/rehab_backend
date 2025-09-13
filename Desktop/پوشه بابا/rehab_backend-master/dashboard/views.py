from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from patients.models import Patient
from patients.medication_models import DrugAppointment, Prescription, MedicationDispensing, DrugInventory
from django.db.models import Count, Q, F, Sum
from datetime import datetime, timedelta
from django.utils import timezone

@login_required
def dashboard(request):
    # Get current date and calculate date ranges
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    
    # Get statistics
    stats = {
        'total_patients': Patient.objects.count(),
        'today_appointments': DrugAppointment.objects.filter(date=today).count(),
        'active_prescriptions': Prescription.objects.filter(
            end_date__gte=today,
            start_date__lte=today
        ).count(),
        'total_dispensed': MedicationDispensing.objects.filter(
            dispensing_date=today
        ).aggregate(total=Sum('quantity'))['total'] or 0,
    }
    
    # Prepare recent activities
    recent_activities = []
    
    # Add recent appointments to activities
    recent_appointments = (DrugAppointment.objects
                          .select_related('patient')
                          .filter(date__gte=today)
                          .order_by('date')[:5])
    
    for appointment in recent_appointments:
        recent_activities.append({
            'type': 'primary',
            'icon': 'bx-calendar',
            'title': f'نوبت جدید برای {appointment.patient.full_name if hasattr(appointment.patient, "full_name") else "بیمار"}',
            'description': f'تاریخ ویزیت: {appointment.date.strftime("%Y/%m/%d")}',
            'time': 'امروز' if appointment.date == today else appointment.date.strftime("%Y/%m/%d")
        })
    
    # Add recent patients to activities
    recent_patients = Patient.objects.order_by('-created_at')[:3]
    for patient in recent_patients:
        recent_activities.append({
            'type': 'success',
            'icon': 'bx-user-plus',
            'title': f'بیمار جدید ثبت شد',
            'description': f'{patient.full_name} به سیستم اضافه شد',
            'time': 'امروز' if patient.created_at.date() == today else patient.created_at.strftime("%Y/%m/%d")
        })
    
    # Add some sample activities if needed
    if not recent_activities:
        recent_activities = [
            {
                'type': 'warning',
                'icon': 'bx-bell',
                'title': 'خوش آمدید به سیستم مدیریت بیماران',
                'description': 'سیستم آماده استفاده است',
                'time': 'هم اکنون'
            }
        ]
    
    # Sort activities by time (newest first)
    recent_activities.sort(key=lambda x: x.get('time', ''), reverse=True)
    
    # Get low stock alerts
    low_stock_items = DrugInventory.objects.filter(
        current_stock__lte=F('minimum_stock')
    ).select_related('medication_type')
    
    # Add low stock alerts to activities
    for item in low_stock_items[:3]:  # Show max 3 low stock items
        recent_activities.append({
            'type': 'danger',
            'icon': 'bx-error',
            'title': 'هشدار موجودی کم',
            'description': f'موجودی {item.medication_type.name} به {item.current_stock} رسیده است',
            'time': 'هم اکنون'
        })
    
    # Sort activities by time (newest first)
    recent_activities.sort(key=lambda x: x.get('time', ''), reverse=True)
    
    context = {
        'title': 'داشبورد مدیریتی',
        'stats': stats,
        'recent_activities': recent_activities[:5],  # Show only 5 most recent activities
        'low_stock_items': low_stock_items,
    }
    
    return render(request, 'dashboard/dashboard_new.html', context)
