import requests
import json

# آدرس سرویس شبیه‌ساز پوز
# در یک پروژه واقعی، این آدرس باید در فایل settings.py تعریف شود
POS_SIMULATOR_URL = "http://127.0.0.1:8001/api/v1/pay"

def send_payment_to_pos(payment_id: int, amount: float) -> dict:
    """
    یک درخواست پرداخت را به شبیه‌ساز دستگاه پوز ارسال می‌کند.

    Args:
        payment_id: شناسه یکتای رکورد پرداخت در دیتابیس.
        amount: مبلغ پرداخت.

    Returns:
        یک دیکشنری شامل پاسخ دریافت شده از سرویس پوز.
    """
    payload = {
        "amount": amount,
        "request_id": str(payment_id)  # از شناسه پرداخت به عنوان شناسه درخواست استفاده می‌کنیم
    }

    try:
        # ارسال درخواست به سرویس پوز با مهلت زمانی ۱۰ ثانیه
        response = requests.post(POS_SIMULATOR_URL, json=payload, timeout=10)
        response.raise_for_status()  # اگر خطای HTTP رخ دهد، استثنا ایجاد می‌کند
        return response.json()
    except requests.exceptions.RequestException as e:
        # مدیریت خطاهای شبکه مانند عدم اتصال، تایم‌اوت و غیره
        print(f"Error connecting to POS service: {e}")
        return {
            "status": "failed",
            "message": f"خطا در ارتباط با سرویس پوز: {e}",
            "transaction_id": None,
            "pos_data": None
        }
