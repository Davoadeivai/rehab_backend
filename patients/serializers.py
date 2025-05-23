from rest_framework import serializers
from .models import Patient, Family, Medication

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class FamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = '__all__'

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'
        
# class بیمارSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = بیمار
#         fields = '__all__'

# class مراجعهSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = مراجعه
#         fields = '__all__'