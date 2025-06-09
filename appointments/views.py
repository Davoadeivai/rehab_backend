from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Appointment
from patients.models import Patient
import jdatetime
import json
from django.views.decorators.csrf import csrf_exempt

@login_required
def calendar_view(request):
    """نمایش تقویم نوبت‌دهی با لیست بیماران برای ثبت نوبت"""
    patients = Patient.objects.all()
    return render(request, 'appointments/calendar.html', {'patients': patients})

@login_required
def appointments_json(request):
    appointments = Appointment.objects.select_related('patient').all()
    events = []
    for appt in appointments:
        events.append({
            'id': appt.id,
            'title': f"{appt.patient.first_name} {appt.patient.last_name}",
            'start': appt.appointment_date.strftime('%Y-%m-%d'),
            'color': '#4e73df' if appt.status == 'completed' else '#e74c3c',
            'extendedProps': {
                'status': appt.status,
                'patient_id': appt.patient.id,
                'notes': appt.notes,
            }
        })
    return JsonResponse(events, safe=False)

@login_required
def create_appointment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        date_str = data.get('date')
        patient = get_object_or_404(Patient, id=patient_id)
        try:
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    jy, jm, jd = map(int, parts)
                    gdate = jdatetime.date(jy, jm, jd).togregorian()
                else:
                    return JsonResponse({'status': 'error', 'msg': 'فرمت تاریخ نامعتبر است.'}, status=400)
            else:
                return JsonResponse({'status': 'error', 'msg': 'فرمت تاریخ نامعتبر است.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'خطا در تبدیل تاریخ: {e}'}, status=400)
        appt = Appointment.objects.create(patient=patient, appointment_date=gdate)
        return JsonResponse({'status': 'ok', 'id': appt.id})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
@csrf_exempt
def appointment_detail(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    if request.method == 'GET':
        return JsonResponse({
            'id': appt.id,
            'patient_id': appt.patient.id,
            'patient_name': f"{appt.patient.first_name} {appt.patient.last_name}",
            'appointment_date': appt.appointment_date.strftime('%Y-%m-%d'),
            'status': appt.status,
            'notes': appt.notes,
        })
    elif request.method == 'POST':
        data = json.loads(request.body)
        date_str = data.get('date')
        status = data.get('status', appt.status)
        notes = data.get('notes', appt.notes)
        try:
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    jy, jm, jd = map(int, parts)
                    gdate = jdatetime.date(jy, jm, jd).togregorian()
                else:
                    return JsonResponse({'status': 'error', 'msg': 'فرمت تاریخ نامعتبر است.'}, status=400)
            else:
                return JsonResponse({'status': 'error', 'msg': 'فرمت تاریخ نامعتبر است.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'خطا در تبدیل تاریخ: {e}'}, status=400)
        appt.appointment_date = gdate
        appt.status = status
        appt.notes = notes
        appt.save()
        return JsonResponse({'status': 'ok'})
    elif request.method == 'DELETE':
        appt.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400) 