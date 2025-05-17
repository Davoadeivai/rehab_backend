from rest_framework import viewsets
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from .models import Patient
from django.http import HttpResponse
from django.template.loader import get_template
# from xhtml2pdf import pisa
from weasyprint import HTML
from django.contrib.auth import logout
from .forms import PatientForm


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