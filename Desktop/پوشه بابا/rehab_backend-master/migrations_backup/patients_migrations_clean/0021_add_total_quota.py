from django.db import migrations, models
import django.core.validators

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0020_patient_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='drugquota',
            name='total_quota',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0, 'سهمیه کل نمی‌تواند منفی باشد')], verbose_name='سهمیه کل'),
        ),
    ]
