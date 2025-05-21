from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models

class Patient(models.Model):
    row_number = models.PositiveIntegerField(verbose_name="ردیف", null=True, blank=True)
    full_name = models.CharField(max_length=100, verbose_name="نام و نام خانوادگی")
    file_number = models.CharField(max_length=50, verbose_name="شماره پرونده")
    system_code = models.CharField(max_length=50, verbose_name="کد سامانه")

    dose_b2_1 = models.CharField(max_length=20, verbose_name="B2 ۱", null=True, blank=True)
    dose_b2_2 = models.CharField(max_length=20, verbose_name="B2 ۲", null=True, blank=True)
    dose_b2_3 = models.CharField(max_length=20, verbose_name="B2 ۳", null=True, blank=True)
    dose_0_4 = models.CharField(max_length=20, verbose_name="دوز 0.4", null=True, blank=True)
    dose_40mg = models.CharField(max_length=20, verbose_name="دوز 40mg", null=True, blank=True)
    dose_20mg = models.CharField(max_length=20, verbose_name="دوز 20mg", null=True, blank=True)
    dose_5mg = models.CharField(max_length=20, verbose_name="دوز 5mg", null=True, blank=True)

    th = models.CharField(max_length=20, verbose_name="T.H", null=True, blank=True)
    doctor_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="نام پزشک")
    payment_amount = models.BigIntegerField(verbose_name="هزینه پرداختی")
    receiver_signature = models.CharField(max_length=100, verbose_name="امضاء دریافت‌کننده")
    date = models.DateField(default=timezone.now)
    

    def __str__(self):
        return f"{self.full_name} - {self.date}"

class Family(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='شماره_پرونده')
    members_count = models.IntegerField(_('تعداد اعضا'))
    support_type = models.CharField(_('نوع حمایت'), max_length=50)
    recorded_deviations = models.TextField(_('انحرافات ثبت شده'))

    class Meta:
        db_table = 'خانواده'

class Medication(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, db_column='شماره_پرونده')
    dosage_40mg = models.IntegerField(_('دوز ۴۰mg'))
    dosage_20mg = models.IntegerField(_('دوز ۲۰mg'))
    dosage_5mg = models.IntegerField(_('دوز ۵mg'))

    class Meta:
        db_table = 'داروها'
        
# srart patiet see center helth

        
# from django.db import models
class SubstanceAbuseRecord(models.Model):
      
   File_number=models.CharField(max_length=100, verbose_name='شماره پرونده')
   full_name= models.CharField(max_length=100, verbose_name='نام و نام خانوادگی')
   national_code = models.CharField(max_length=10, verbose_name='کد ملی')
   age_patient =models.CharField(max_length=100, verbose_name='سن')
   age_of_onset = models.PositiveIntegerField(verbose_name='سن شروع مصرف')
#    substance_type = models.CharField(max_length=50,choices=SUBSTANCE_TYPE_CHOICES,verbose_name='نوع مواد مصرفی')
#    Type_of_treatment = CharField(max_length=100, verbose_name='نوع درمان ')
   address_numberphone = models.TextField(verbose_name='آدرس و ثبت')
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)
   description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
   
   def __str__(self):
    return f"{self.File_number} - {self.national_code}"

    
#   SUBSTANCE_TYPE_CHOICES = [
#         ('opium', 'تریاک'),
#         ('heroin', 'هروئین'),
#         ('meth', 'شیشه'),
#         ('cannabis', 'حشیش/ماریجوانا'),
#         ('alcohol', 'الکل'),
#         ('other', 'سایر'),
#     ]
   
    
     
    
   
     
     
   
    
    
    
    
  
   
   
   

    
    
   
   
    

