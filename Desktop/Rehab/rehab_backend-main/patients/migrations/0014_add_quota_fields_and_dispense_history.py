from django.db import migrations, models
import django_jalali.db.models as jmodels
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('patients', '0013_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='weekly_quota',
            field=models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='سهمیه هفتگی'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='monthly_quota',
            field=models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='سهمیه ماهانه'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='allocated_amount',
            field=models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='مقدار اختصاص یافته در این نسخه'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='received_amount',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2, verbose_name='مقدار دریافتی تا کنون'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='remaining_quota',
            field=models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='سهمیه باقی‌مانده این نسخه'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='period_type',
            field=models.CharField(default='week', max_length=10, choices=[('day', 'روزانه'), ('week', 'هفتگی'), ('month', 'ماهانه')], verbose_name='نوع بازه سهمیه'),
        ),
        migrations.CreateModel(
            name='DrugDispenseHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dispense_date', jmodels.jDateField(verbose_name='تاریخ دریافت')),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2, verbose_name='مقدار دریافتی')),
                ('period_type', models.CharField(max_length=10, choices=[('day', 'روزانه'), ('week', 'هفتگی'), ('month', 'ماهانه')], default='week', verbose_name='نوع بازه')),
                ('period_label', models.CharField(max_length=50, verbose_name='برچسب بازه (مثلاً هفته اول فروردین)')),
                ('remaining_quota', models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name='سهمیه باقی‌مانده پس از دریافت')),
                ('created_at', jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.patient', verbose_name='بیمار')),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.prescription', verbose_name='نسخه')),
                ('medication_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='patients.medicationtype', verbose_name='نوع دارو')),
            ],
            options={
                'verbose_name': 'تاریخچه دریافت دارو',
                'verbose_name_plural': 'تاریخچه دریافت داروها',
            },
        ),
    ] 