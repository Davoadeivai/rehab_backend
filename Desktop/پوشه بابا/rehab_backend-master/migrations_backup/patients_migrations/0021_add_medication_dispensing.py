from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0020_patient_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicationDispensing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dispensing_date', models.DateField(verbose_name='تاریخ تحویل')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01, 'مقدار باید بزرگتر از صفر باشد')], verbose_name='مقدار تحویلی')),
                ('unit_price', models.DecimalField(decimal_places=0, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0, 'قیمت نمی‌تواند منفی باشد')], verbose_name='قیمت واحد (ریال)')),
                ('total_price', models.DecimalField(decimal_places=0, editable=False, max_digits=15, verbose_name='جمع کل (ریال)')),
                ('dispensing_type', models.CharField(choices=[('normal', 'عادی'), ('emergency', 'اضطراری'), ('special', 'ویژه')], default='normal', max_length=20, verbose_name='نوع تحویل')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dispensing_records', to=settings.AUTH_USER_MODEL, verbose_name='ثبت کننده')),
                ('medication_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dispensings', to='patients.medicationtype', verbose_name='نوع دارو')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medication_dispensings', to='patients.patient', verbose_name='بیمار')),
            ],
            options={
                'verbose_name': 'تحویل دارو',
                'verbose_name_plural': 'تحویل‌های دارویی',
                'ordering': ['-dispensing_date', '-created_at'],
            },
        ),
    ]
