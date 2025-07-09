from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal
from django.core.validators import MinValueValidator


def set_default_monthly_quota(apps, schema_editor):
    """Set default monthly_quota for existing DrugQuota records"""
    DrugQuota = apps.get_model('patients', 'DrugQuota')
    
    # For existing records, set monthly_quota to the same value as remaining_quota
    for quota in DrugQuota.objects.all():
        quota.monthly_quota = quota.remaining_quota or Decimal('0.00')
        quota.save()


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0016_add_medication_type_to_drugquota'),
    ]

    operations = [
        migrations.AddField(
            model_name='drugquota',
            name='monthly_quota',
            field=models.DecimalField(
                "سهمیه ماهانه",
                max_digits=10,
                decimal_places=2,
                null=True,
                validators=[
                    MinValueValidator(
                        Decimal('0.00'),
                        message="مقدار سهمیه باید بزرگتر از صفر باشد"
                    )
                ],
                help_text="سهمیه ماهانه برای این دارو"
            ),
        ),
        migrations.RunPython(
            set_default_monthly_quota,
            # No reverse code needed as this is a data migration
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='drugquota',
            name='monthly_quota',
            field=models.DecimalField(
                "سهمیه ماهانه",
                max_digits=10,
                decimal_places=2,
                validators=[
                    MinValueValidator(
                        Decimal('0.00'),
                        message="مقدار سهمیه باید بزرگتر از صفر باشد"
                    )
                ],
                help_text="سهمیه ماهانه برای این دارو"
            ),
        ),
    ]
