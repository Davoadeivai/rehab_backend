# patients/utils.py
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from .medication_models import MedicationDistribution
import jdatetime

def calculate_medication_usage(patient_id, days):
    """
    محاسبه میزان مصرف دارو در بازه زمانی مشخص
    """
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    return MedicationDistribution.objects.filter(
        prescription__patient__file_number=patient_id,
        distribution_date__range=(start_date, end_date)
    ).aggregate(
        total_amount=Sum('amount')
    )

def format_jalali_date(date_obj, include_time=False):
    """
    تبدیل تاریخ به فرمت فارسی
    """
    if not date_obj:
        return ""
    
    if isinstance(date_obj, jdatetime.datetime) or isinstance(date_obj, jdatetime.date):
        j_date = date_obj
    else:
        if isinstance(date_obj, timezone.datetime):
            j_date = jdatetime.datetime.fromgregorian(datetime=date_obj)
        else:
            j_date = jdatetime.date.fromgregorian(date=date_obj)
    
    # تبدیل اعداد به فارسی
    persian_numbers = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    
    if include_time and isinstance(j_date, jdatetime.datetime):
        date_str = j_date.strftime('%Y/%m/%d %H:%M')  # Removed seconds for cleaner display
    else:
        # Using strftime with zero-padded month and day
        date_str = j_date.strftime('%Y/%m/%d')
    
    # تبدیل اعداد به فارسی
    for en, fa in persian_numbers.items():
        date_str = date_str.replace(en, fa)
    
    return date_str

def format_jalali_month_name(date_obj):
    """
    نمایش نام ماه به فارسی
    """
    if not date_obj:
        return ""
    
    if isinstance(date_obj, jdatetime.datetime) or isinstance(date_obj, jdatetime.date):
        j_date = date_obj
    else:
        if isinstance(date_obj, timezone.datetime):
            j_date = jdatetime.datetime.fromgregorian(datetime=date_obj)
        else:
            j_date = jdatetime.date.fromgregorian(date=date_obj)
    
    persian_months = {
        1: 'فروردین', 2: 'اردیبهشت', 3: 'خرداد',
        4: 'تیر', 5: 'مرداد', 6: 'شهریور',
        7: 'مهر', 8: 'آبان', 9: 'آذر',
        10: 'دی', 11: 'بهمن', 12: 'اسفند'
    }
    
    return persian_months.get(j_date.month, '')

def format_jalali_full_date(date_obj):
    """
    نمایش کامل تاریخ به فارسی (مثال: ۱۵ مرداد ۱۴۰۲)
    """
    if not date_obj:
        return ""
    
    if isinstance(date_obj, jdatetime.datetime) or isinstance(date_obj, jdatetime.date):
        j_date = date_obj
    else:
        if isinstance(date_obj, timezone.datetime):
            j_date = jdatetime.datetime.fromgregorian(datetime=date_obj)
        else:
            j_date = jdatetime.date.fromgregorian(date=date_obj)
    
    persian_numbers = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    
    # Zero-pad day for consistent formatting
    day = str(j_date.day).zfill(2)
    month = format_jalali_month_name(j_date)
    year = str(j_date.year)
    
    for en, fa in persian_numbers.items():
        day = day.replace(en, fa)
        year = year.replace(en, fa)
    
    return f"{day} {month} {year}"

def format_number(number):
    """
    تبدیل اعداد به فرمت فارسی با جداکننده هزارگان
    مثال: 1000000 -> ۱,۰۰۰,۰۰۰
    """
    if number is None:
        return "۰"
    
    # تبدیل به رشته و اضافه کردن کاما
    str_number = "{:,}".format(int(number))
    
    # تبدیل اعداد به فارسی
    persian_numbers = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
    }
    
    result = ""
    for char in str_number:
        if char in persian_numbers:
            result += persian_numbers[char]
        else:
            result += char
    
    return result
