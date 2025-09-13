from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import (
    Patient, MedicationType, DrugQuota, DrugInventory, 
    MedicationDispensing, InventoryLog, Alert
)
from .forms import MedicationDispensingForm
from .utils import send_alert

@login_required
@permission_required('patients.view_medicationdispensing')
def medication_dispensing_list(request):
    """
    لیست تحویل‌های دارویی
    """
    query = request.GET.get('q', '')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    medication_type_id = request.GET.get('medication_type')
    
    dispensings = MedicationDispensing.objects.select_related(
        'patient', 'medication_type', 'created_by'
    ).order_by('-dispensing_date')
    
    if query:
        dispensings = dispensings.filter(
            Q(patient__first_name__icontains=query) |
            Q(patient__last_name__icontains=query) |
            Q(patient__national_code__icontains=query) |
            Q(notes__icontains=query)
        )
    
    if date_from:
        dispensings = dispensings.filter(dispensing_date__date__gte=date_from)
    
    if date_to:
        dispensings = dispensings.filter(dispensing_date__date__lte=date_to)
    
    if medication_type_id:
        dispensings = dispensings.filter(medication_type_id=medication_type_id)
    
    # Pagination
    paginator = Paginator(dispensings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    medication_types = MedicationType.objects.all()
    
    context = {
        'page_title': _('لیست تحویل‌های دارویی'),
        'page_obj': page_obj,
        'medication_types': medication_types,
        'query': query,
        'date_from': date_from or '',
        'date_to': date_to or '',
        'selected_medication': int(medication_type_id) if medication_type_id else '',
    }
    
    return render(request, 'patients/medication_dispensing_list.html', context)

@login_required
@permission_required('patients.add_medicationdispensing')
def medication_dispensing_create(request, patient_id=None):
    """
    ثبت تحویل جدید دارو به بیمار
    """
    patient = None
    if patient_id:
        patient = get_object_or_404(Patient, pk=patient_id)
    
    if request.method == 'POST':
        form = MedicationDispensingForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    dispensing = form.save(commit=False)
                    dispensing.created_by = request.user
                    dispensing.save()
                    
                    messages.success(request, _('تحویل دارو با موفقیت ثبت شد.'))
                    return redirect('patients:medication_dispensing_list')
                    
            except Exception as e:
                messages.error(request, f'خطا در ثبت تحویل دارو: {str(e)}')
    else:
        initial = {}
        if patient:
            initial['patient'] = patient
            
        form = MedicationDispensingForm(initial=initial, user=request.user)
    
    context = {
        'page_title': _('ثبت تحویل داروی جدید'),
        'form': form,
        'patient': patient,
    }
    
    return render(request, 'patients/medication_dispensing_form.html', context)

@login_required
@permission_required('patients.change_medicationdispensing')
def medication_dispensing_edit(request, pk):
    """
    ویرایش تحویل دارو
    """
    dispensing = get_object_or_404(MedicationDispensing, pk=pk)
    
    if request.method == 'POST':
        form = MedicationDispensingForm(
            request.POST, 
            instance=dispensing, 
            user=request.user
        )
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Store old values for rollback if needed
                    old_quantity = dispensing.quantity
                    old_medication = dispensing.medication_type
                    
                    # Update the dispensing
                    dispensing = form.save(commit=False)
                    dispensing.updated_by = request.user
                    dispensing.save()
                    
                    messages.success(request, _('تحویل دارو با موفقیت ویرایش شد.'))
                    return redirect('patients:medication_dispensing_list')
                    
            except Exception as e:
                messages.error(request, f'خطا در ویرایش تحویل دارو: {str(e)}')
    else:
        form = MedicationDispensingForm(instance=dispensing, user=request.user)
    
    context = {
        'page_title': _('ویرایش تحویل دارو'),
        'form': form,
        'dispensing': dispensing,
    }
    
    return render(request, 'patients/medication_dispensing_form.html', context)

@login_required
@permission_required('patients.delete_medicationdispensing')
def medication_dispensing_delete(request, pk):
    """
    حذف تحویل دارو
    """
    dispensing = get_object_or_404(MedicationDispensing, pk=pk)
    
    if request.method == 'POST':
        try:
            dispensing.delete()
            messages.success(request, _('تحویل دارو با موفقیت حذف شد.'))
        except Exception as e:
            messages.error(request, f'خطا در حذف تحویل دارو: {str(e)}')
        
        return redirect('patients:medication_dispensing_list')
    
    context = {
        'page_title': _('حذف تحویل دارو'),
        'object': dispensing,
    }
    
    return render(request, 'patients/confirm_delete.html', context)

@login_required
@permission_required('patients.view_medicationdispensing')
def medication_dispensing_detail(request, pk):
    """
    جزئیات تحویل دارو
    """
    dispensing = get_object_or_404(
        MedicationDispensing.objects.select_related(
            'patient', 'medication_type', 'created_by'
        ), 
        pk=pk
    )
    
    context = {
        'page_title': _('جزئیات تحویل دارو'),
        'dispensing': dispensing,
    }
    
    return render(request, 'patients/medication_dispensing_detail.html', context)

@login_required
@require_http_methods(["GET"])
def get_patient_medication_info(request, patient_id):
    """
    دریافت اطلاعات دارویی بیمار برای استفاده در فرم تحویل دارو
    """
    patient = get_object_or_404(Patient, pk=patient_id)
    
    # دریافت سهمیه‌های فعال بیمار
    today = timezone.now().date()
    quotas = DrugQuota.objects.filter(
        patient=patient,
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    ).select_related('medication_type')
    
    # دریافت موجودی داروها
    medication_data = []
    for quota in quotas:
        try:
            inventory = DrugInventory.objects.get(
                medication_type=quota.medication_type
            )
            medication_data.append({
                'id': quota.medication_type.id,
                'name': str(quota.medication_type),
                'unit': quota.medication_type.unit,
                'quota': float(quota.remaining_quota),
                'stock': float(inventory.current_stock),
                'unit_price': float(quota.medication_type.unit_price) if hasattr(quota.medication_type, 'unit_price') else 0,
            })
        except DrugInventory.DoesNotExist:
            continue
    
    return JsonResponse({
        'success': True,
        'patient': {
            'id': patient.id,
            'full_name': patient.get_full_name(),
            'national_code': patient.national_code,
        },
        'medications': medication_data,
    })

@login_required
@require_http_methods(["GET"])
def get_medication_stock(request, medication_type_id):
    """
    دریافت موجودی فعلی یک دارو
    """
    try:
        inventory = DrugInventory.objects.get(medication_type_id=medication_type_id)
        return JsonResponse({
            'success': True,
            'stock': float(inventory.current_stock),
            'unit': inventory.medication_type.unit,
        })
    except DrugInventory.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'موجودی یافت نشد',
        }, status=404)
