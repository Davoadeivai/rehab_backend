from django.db import migrations, models
from django.conf import settings


def set_default_user_for_inventory_logs(apps, schema_editor):
    InventoryLog = apps.get_model('pharmacy', 'InventoryLog')
    User = apps.get_model(settings.AUTH_USER_MODEL)
    
    # Get the first superuser or create a default one if none exists
    default_user = User.objects.filter(is_superuser=True).first()
    if not default_user and User.objects.exists():
        default_user = User.objects.first()
    elif not default_user:
        # Create a default user if no users exist
        default_user = User.objects.create(
            username='admin',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            email='admin@example.com'
        )
    
    # Update all null user references
    InventoryLog.objects.filter(user__isnull=True).update(user=default_user)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pharmacy', '0005_drugpurchase_interval_days_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorylog',
            name='user',
            field=models.ForeignKey(
                on_delete=models.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                null=True,
                blank=True,
                verbose_name='کاربر',
                related_name='pharmacy_inventory_logs'
            ),
        ),
        migrations.RunPython(set_default_user_for_inventory_logs, migrations.RunPython.noop),
    ]
