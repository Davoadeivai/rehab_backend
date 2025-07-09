import random
from .models import PhoneVerification

def generate_verification_code():
    """یک کد تایید ۶ رقمی تصادفی ایجاد می‌کند."""
    return str(random.randint(100000, 999999))

def send_verification_code(phone_number):
    """
    یک کد تایید ایجاد کرده، آن را ذخیره می‌کند و با چاپ در کنسول آن را «ارسال» می‌کند.
    """
    if not phone_number:
        return False, "شماره موبایل نمی‌تواند خالی باشد."

    code = generate_verification_code()
    try:
        # برای سادگی، کدهای قدیمی برای همین شماره را قبل از ایجاد کد جدید حذف می‌کنیم.
        PhoneVerification.objects.filter(phone_number=phone_number).delete()
        
        PhoneVerification.objects.create(
            phone_number=phone_number,
            code=code
        )
        # در یک برنامه واقعی، در اینجا با یک درگاه پیامک ادغام می‌شوید.
        # در حال حاضر، ما فقط آن را برای توسعه در کنسول چاپ می‌کنیم.
        print("-" * 50)
        print(f"[شبیه‌ساز پیامک] ارسال کد تایید به شماره: {phone_number}")
        print(f"[شبیه‌ساز پیامک] کد: {code}")
        print("-" * 50)
        return True, "کد تایید با موفقیت ارسال شد."
    except Exception as e:
        print(f"خطا در ایجاد کد تایید برای {phone_number}: {e}")
        return False, "ارسال کد تایید با خطا مواجه شد."
