from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0020_patient_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='addiction_start_age',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='سن شروع اعتیاد', help_text='سن شروع مصرف مواد مخدر (به سال)'),
        ),
    ]
