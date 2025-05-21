from rest_framework import viewsets
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from .models import Patient,SubstanceAbuseRecord
from django.http import HttpResponse
from django.template.loader import get_template
# from xhtml2pdf import pisa
from weasyprint import HTML
from django.contrib.auth import logout
from .forms import PatientForm, FamilyForm, MedicationForm,SubstanceAbuseRecordForm
from django.urls import reverse

from django.shortcuts import render, redirect

from .models import Patient, Family, Medication
from .serializers import PatientSerializer, FamilySerializer, MedicationSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class FamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all()
    serializer_class = FamilySerializer

class MedicationViewSet(viewsets.ModelViewSet):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer

# Create your views here.
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/patient_list.html', {'patients': patients})

 
def generate_patient_pdf(request,pk):
    patient=get_object_or_404(Patient, pk=pk)
    template_path =get_template('patients/patient_pdf.html')
    html_string = template_path.render({'patient': patient})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="patient.pdf"'
    
    HTML(string=html_string).write_pdf(response, stylesheets=['static/css/pdf.css'])
    return response


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # اینجا صفحه‌ایه که کاربر بعد از ورود می‌ره
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    return render(request, 'patients/login.html')

def dashboard_view(request):
    # return HttpResponse("به داشبورد خوش آمدید!")
    if request.user.is_authenticated:
        return render(request, 'patients/dashboard.html')
    else:
        return redirect('login')  # اگر کاربر وارد نشده باشد، به صفحه ورود هدایت می‌شود

# add logout view
def logout_view(request):
    logout(request)
    return redirect('login')  # بعد از خروج به صفحه ورود هدایت می‌شود

# add patient form view
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'بیمار با موفقیت ثبت شد.')
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'patients/patient_create.html', {'form': form})


def patient_detail_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'patients/patient_detail.html', {'patient': patient})


def patient_edit_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'بیمار با موفقیت ویرایش شد.')
            return redirect('patient_detail', pk=pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_edit.html', {'form': form})

def patient_delete_view(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        patient.delete()
        messages.success(request, 'بیمار با موفقیت حذف شد.')
        return redirect('patient_list')
    return render(request, 'patients/patient_delete.html', {'patient': patient})


def add_family(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = FamilyForm(request.POST)
        if form.is_valid():
            family = form.save(commit=False)
            family.patient = patient
            family.save()
            messages.success(request, 'خانواده با موفقیت ثبت شد.')
            return redirect('patient_detail', pk=patient_id)
    else:
        form = FamilyForm()
    return render(request, 'patients/family_form.html', {'form': form, 'patient': patient})


def add_medication(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'دارو با موفقیت ثبت شد.')
            return redirect('patient_list')
    else:
        form = MedicationForm()
    return render(request, 'patients/medication_form.html', {'form': form})


def record_list(request):
    records = SubstanceAbuseRecord.objects.all().order_by('-created_at')
    return render(request, 'patients/record_list.html', {'records': records})

def add_record(request):
    pass
#     if request.method == 'POST':
#         form = SubstanceAbuseRecordForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('record_list')
#     else:
#         form = SubstanceAbuseRecordForm()
    
#     return render(request, 'substance_abuse/add_record.html', {'form': form})

# def edit_record(request, pk):
#     record = SubstanceAbuseRecord.objects.get(pk=pk)
#     if request.method == 'POST':
#         form = SubstanceAbuseRecordForm(request.POST, instance=record)
#         if form.is_valid():
#             form.save()
#             return redirect('record_list')
#     else:
#         form = SubstanceAbuseRecordForm(instance=record)
    
#     return render(request, 'substance_abuse/edit_record.html', {'form': form})

# def delete_record(request, pk):
#     record = SubstanceAbuseRecord.objects.get(pk=pk)
#     if request.method == 'POST':
#         record.delete()
#         return redirect('record_list')
#     return render(request, 'substance_abuse/delete_record.html', {'record': record})