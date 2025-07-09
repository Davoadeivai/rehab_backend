from django.db import migrations, models
import django_jalali.db.models
from django.utils import timezone
from datetime import timedelta

def create_default_medication_type(apps, schema_editor):
    """Create a default medication type if none exists."""
    MedicationType = apps.get_model('patients', 'MedicationType')
    if not MedicationType.objects.exists():
        MedicationType.objects.create(
            name='متادون',
            description='داروی پیش‌فرض',
            unit='میلی‌لیتر',
            default_dose=10.0
        )

def update_drug_quota_dates(apps, schema_editor):
    """Set default dates for existing DrugQuota records."""
    DrugQuota = apps.get_model('patients', 'DrugQuota')
    today = timezone.now().date()
    
    for quota in DrugQuota.objects.all():
        if not hasattr(quota, 'start_date') or not quota.start_date:
            quota.start_date = today
        if not hasattr(quota, 'end_date') or not quota.end_date:
            quota.end_date = today + timedelta(days=30)
        if not hasattr(quota, 'monthly_quota') or not quota.monthly_quota:
            quota.monthly_quota = quota.remaining_quota or 0
        if not hasattr(quota, 'is_active'):
            quota.is_active = True
        quota.save(update_fields=['start_date', 'end_date', 'monthly_quota', 'is_active'])

class Migration(migrations.Migration):
    dependencies = [
        ('patients', '0013_payment_status'),
    ]

    operations = [
        # Add the new fields with null=True first
        migrations.AddField(
            model_name='drugquota',
            name='created_at',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True, null=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AddField(
            model_name='drugquota',
            name='end_date',
            field=django_jalali.db.models.jDateField(null=True, verbose_name='تاریخ پایان سهمیه'),
        ),
        migrations.AddField(
            model_name='drugquota',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='فعال'),
        ),
        migrations.AddField(
            model_name='drugquota',
            name='start_date',
            field=django_jalali.db.models.jDateField(null=True, verbose_name='تاریخ شروع سهمیه'),
        ),
        migrations.AddField(
            model_name='drugquota',
            name='updated_at',
            field=django_jalali.db.models.jDateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی'),
        ),
        
        # Run data migration to set values for existing records
        migrations.RunPython(create_default_medication_type, migrations.RunPython.noop),
        migrations.RunPython(update_drug_quota_dates, migrations.RunPython.noop),
        
        # Now alter the fields to be non-nullable
        migrations.AlterField(
            model_name='drugquota',
            name='created_at',
            field=django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد'),
        ),
        migrations.AlterField(
            model_name='drugquota',
            name='end_date',
            field=django_jalali.db.models.jDateField(verbose_name='تاریخ پایان سهمیه'),
        ),
        migrations.AlterField(
            model_name='drugquota',
            name='start_date',
            field=django_jalali.db.models.jDateField(verbose_name='تاریخ شروع سهمیه'),
        ),
    ]
