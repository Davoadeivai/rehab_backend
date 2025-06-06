# Generated by Django 5.2.2 on 2025-06-04 18:59

import django.db.models.deletion
import django_jalali.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0005_patient_created_at_patient_updated_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DrugInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_stock', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='موجودی فعلی')),
                ('minimum_stock', models.DecimalField(decimal_places=2, default=10, help_text='هشدار زمانی که موجودی به این مقدار برسد', max_digits=10, verbose_name='حداقل موجودی')),
                ('last_updated', django_jalali.db.models.jDateTimeField(auto_now=True, verbose_name='آخرین به\u200cروزرسانی')),
                ('medication_type', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='inventory', to='patients.medicationtype', verbose_name='نوع دارو')),
            ],
            options={
                'verbose_name': 'موجودی دارو',
                'verbose_name_plural': 'موجودی داروها',
            },
        ),
    ]
