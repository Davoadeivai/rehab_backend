from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from ..models import Patient
from ..medication_models import (
    MedicationType,
    Prescription,
    MedicationDistribution,
    Payment,
    DrugQuota,
    DrugInventory
)
from ..serializers import (
    PatientSerializer,
    RegisterSerializer,
    LoginSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    MedicationTypeSerializer,
    PrescriptionSerializer,
    MedicationDistributionSerializer,
    PaymentSerializer,
)

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @action(detail=False, methods=['post'], url_path='login', url_name='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status=status.HTTP_200_OK)
            return Response({'error': 'نام کاربری یا رمز عبور اشتباه است'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='register', url_name='register')
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('q', '').strip()
        
        if search_query:
            # Search by name, last name, national code, or file number
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(national_code__icontains=search_query) |
                Q(file_number__icontains=search_query)
            )
        return queryset
        
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search patients by name, last name, national code, or file number
        """
        queryset = self.get_queryset()
        
        # Limit results to 10 for performance
        patients = queryset[:10]
        
        # Serialize results with minimal fields
        results = [{
            'id': patient.id,
            'full_name': f'{patient.first_name} {patient.last_name}'.strip(),
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'national_code': patient.national_code,
            'file_number': patient.file_number,
            'url': f'/patients/{patient.id}/',
        } for patient in patients]
        
        return Response({'results': results})

    @action(detail=True, methods=['get'], url_path='medication-info')
    def medication_info(self, request, pk=None):
        patient = self.get_object()
        today = timezone.now().date()

        # Get active drug quotas for the patient
        quotas = DrugQuota.objects.filter(
            patient=patient,
            is_active=True,
            start_date__lte=today,
            end_date__gte=today
        ).select_related('medication_type')

        medication_data = []
        for quota in quotas:
            medication_data.append({
                'id': quota.medication_type.id,
                'name': quota.medication_type.name,
                'unit': quota.medication_type.unit,
                'quota': quota.remaining_quota,
            })

        return Response({
            'success': True,
            'patient': {
                'full_name': patient.get_full_name(),
                'national_code': patient.national_code,
            },
            'medications': medication_data
        })

class MedicationTypeViewSet(viewsets.ModelViewSet):
    queryset = MedicationType.objects.all()
    serializer_class = MedicationTypeSerializer

    @action(detail=True, methods=['get'])
    def stock(self, request, pk=None):
        medication_type = self.get_object()
        try:
            inventory = DrugInventory.objects.get(medication_type=medication_type)
            return Response({
                'success': True,
                'stock': inventory.current_stock,
                'unit': medication_type.unit
            })
        except DrugInventory.DoesNotExist:
            return Response({'success': False, 'message': 'موجودی برای این دارو یافت نشد.'},
                            status=status.HTTP_404_NOT_FOUND)

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

class MedicationDistributionViewSet(viewsets.ModelViewSet):
    queryset = MedicationDistribution.objects.all()
    serializer_class = MedicationDistributionSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class PatientListCreateAPIView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class PatientRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer 