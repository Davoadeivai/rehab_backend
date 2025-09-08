from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, F
from jalali_date import date2jalali
from .medication_models import Alert, Prescription, DrugInventory, DrugQuota

def create_alert(
    alert_type,
    title,
    message,
    related_model=None,
    related_id=None,
    priority='medium',
    due_date=None,
    created_by=None
):
    """
    ایجاد یک هشدار جدید در سیستم
    
    پارامترها:
        alert_type (str): نوع هشدار (از ALERT_TYPES)
        title (str): عنوان هشدار
        message (str): متن پیام هشدار
        related_model (str, اختیاری): نام مدل مرتبط
        related_id (int, اختیاری): شناسه رکورد مرتبط
        priority (str, اختیاری): اولویت هشدار (پیش‌فرض: 'medium')
        due_date (datetime, اختیاری): تاریخ موعد هشدار
        created_by (User, اختیاری): کاربر ایجادکننده هشدار
    
    بازگشت:
        Alert: شیء هشدار ایجاد شده
    """
    return Alert.objects.create(
        alert_type=alert_type,
        title=title,
        message=message,
        related_model=related_model.__name__ if related_model else None,
        related_id=related_id,
        priority=priority,
        due_date=due_date,
        created_by=created_by
    )

def check_prescription_expiry():
    """
    بررسی نسخه‌های در حال انقضا و ایجاد هشدارهای لازم
    """
    today = timezone.now().date()
    warning_days = 3  # تعداد روزهای قبل از انقضا که هشدار داده می‌شود
    
    # پیدا کردن نسخه‌هایی که تا 3 روز دیگر منقضی می‌شوند
    warning_date = today + timedelta(days=warning_days)
    
    expiring_soon = Prescription.objects.filter(
        end_date__gt=today,
        end_date__lte=warning_date
    )
    
    for prescription in expiring_soon:
        days_left = (prescription.end_date - today).days
        create_alert(
            alert_type='prescription_expiry',
            title=f'نسخه در حال انقضا - {prescription.patient.full_name()}',
            message=f'نسخه {prescription.medication_type.name} بیمار {prescription.patient.full_name()} تا {days_left} روز دیگر منقضی می‌شود.',
            related_model=Prescription,
            related_id=prescription.id,
            priority='high' if days_left <= 1 else 'medium',
            due_date=prescription.end_date
        )

def check_low_stock():
    """
    بررسی موجودی کم داروها و ایجاد هشدارهای لازم
    """
    low_stock_items = DrugInventory.objects.filter(
        current_stock__lte=F('minimum_stock')
    )
    
    for item in low_stock_items:
        create_alert(
            alert_type='low_stock',
            title=f'موجودی کم {item.medication_type.name}',
            message=f'موجودی {item.medication_type.name} به {item.current_stock} {item.medication_type.unit} رسیده است. حداقل موجودی: {item.minimum_stock} {item.medication_type.unit}',
            related_model=DrugInventory,
            related_id=item.id,
            priority='high' if item.current_stock <= (item.minimum_stock * 0.5) else 'medium'
        )

def check_quota_warnings():
    """
    بررسی هشدارهای مربوط به سهمیه دارویی
    """
    today = timezone.now().date()
    warning_days = 7  # تعداد روزهای قبل از اتمام سهمیه که هشدار داده می‌شود
    
    # پیدا کردن سهمیه‌هایی که تا 7 روز دیگر به اتمام می‌رسند
    warning_quotas = DrugQuota.objects.filter(
        is_active=True,
        end_date__lte=today + timedelta(days=warning_days),
        remaining_quota__gt=0
    )
    
    for quota in warning_quotas:
        days_left = (quota.end_date - today).days
        create_alert(
            alert_type='quota_warning',
            title=f'هشدار سهمیه - {quota.patient.full_name()}',
            message=f'سهمیه {quota.medication_type.name} بیمار {quota.patient.full_name()} تا {days_left} روز دیگر به اتمام می‌رسد. مقدار باقی‌مانده: {quota.remaining_quota} {quota.medication_type.unit}',
            related_model=DrugQuota,
            related_id=quota.id,
            priority='high' if days_left <= 3 else 'medium',
            due_date=quota.end_date
        )

def check_all_alerts():
    """
    بررسی تمام هشدارهای سیستم
    """
    check_prescription_expiry()
    check_low_stock()
    check_quota_warnings()

def get_user_alerts(user, limit=10, unread_only=False):
    """
    دریافت هشدارهای کاربر
    
    پارامترها:
        user (User): کاربر مورد نظر
        limit (int, اختیاری): حداکثر تعداد هشدارهای بازگشتی
        unread_only (bool, اختیاری): آیا فقط هشدارهای خوانده نشده برگردانده شود؟
    
    بازگشت:
        QuerySet: مجموعه‌ای از هشدارهای کاربر
    """
    alerts = Alert.objects.all()
    
    if unread_only:
        alerts = alerts.filter(is_read=False)
    
    return alerts.order_by('-alert_date')[:limit]

def mark_alert_as_read(alert_id, user):
    """
    علامت‌گذاری یک هشدار به عنوان خوانده شده
    
    پارامترها:
        alert_id (int): شناسه هشدار
        user (User): کاربری که هشدار را می‌خواند
    
    بازگشت:
        bool: آیا عملیات موفقیت‌آمیز بود؟
    """
    try:
        alert = Alert.objects.get(id=alert_id)
        alert.is_read = True
        alert.save(update_fields=['is_read'])
        return True
    except Alert.DoesNotExist:
        return False

def mark_all_alerts_as_read(user):
    """
    علامت‌گذاری تمام هشدارهای کاربر به عنوان خوانده شده
    
    پارامترها:
        user (User): کاربر مورد نظر
    
    بازگشت:
        int: تعداد هشدارهای به‌روزرسانی شده
    """
    return Alert.objects.filter(is_read=False).update(is_read=True)
