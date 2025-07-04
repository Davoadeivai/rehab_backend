# Generated by Django 5.2.2 on 2025-06-13 21:00

from django.db import migrations

def update_default_doses(apps, schema_editor):
    MedicationType = apps.get_model('patients', 'MedicationType')
    medications_to_update = {
        'شربت اپیوم': 5,
        'قرص بوپرنورفین 8 میلی گرم': 1,
        'قرص بوپرنورفین 2 میلی گرم': 1,
        'قرص بوپرنورفین 0.4 میلی گرم': 1,
        'قرص متادون 40 میلی گرم': 0.5,
        'قرص متادون 20 میلی گرم': 1,
        'قرص متادون 5 میلی گرم': 1,
        'شربت متادون': 5,
    }

    for name, dose in medications_to_update.items():
        try:
            med = MedicationType.objects.get(name=name)
            med.default_dose = dose
            med.save()
        except MedicationType.DoesNotExist:
            # دارو وجود ندارد، پس کاری انجام نده
            pass

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0006_medicationtype_default_dose_and_more'),
    ]

    operations = [
        migrations.RunPython(update_default_doses, migrations.RunPython.noop),
    ]
