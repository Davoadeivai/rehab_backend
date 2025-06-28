from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from patients.models import Profile

# The send_verification_code is no longer needed for now
# from patients.sms_service import send_verification_code

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')

            # بررسی اینکه آیا کاربری با این شماره موبایل از قبل وجود دارد
            if Profile.objects.filter(phone_number=phone_number).exists():
                messages.error(request, 'کاربری با این شماره موبایل قبلا ثبت‌نام کرده است.')
                return render(request, 'users/register.html', {'form': form})

            # ذخیره مستقیم کاربر و ورود به سیستم
            user = form.save()
            user.profile.phone_number = phone_number
            user.profile.phone_verified = False # شماره موبایل تایید نشده است
            user.profile.save()

            login(request, user)
            messages.success(request, 'ثبت نام شما با موفقیت انجام شد.')
            return redirect('home') # هدایت به صفحه اصلی
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


# The verify_phone view is now temporarily unused
def verify_phone(request):
    if 'user_registration_data' not in request.session:
        messages.error(request, 'ابتدا باید ثبت‌نام کنید.')
        return redirect('register')

    phone_number = request.session['user_registration_data']['phone_number']

    if request.method == 'POST':
        code = request.POST.get('code')
        if not code:
            messages.error(request, 'کد تایید را وارد کنید.')
        else:
            try:
                # بررسی صحت کد وارد شده
                verification = PhoneVerification.objects.get(phone_number=phone_number, code=code)

                # کد صحیح است، کاربر را ایجاد کن
                user_data = request.session.pop('user_registration_data')

                user = User.objects.create_user(
                    username=user_data['username'],
                    password=user_data['password'],
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )
                # پروفایل به صورت خودکار با سیگنال ساخته شده است
                user.profile.phone_number = user_data['phone_number']
                user.profile.phone_verified = True
                user.profile.save()

                # حذف کد تایید استفاده شده
                verification.delete()

                # ورود خودکار کاربر
                login(request, user)

                messages.success(request, 'ثبت‌نام شما با موفقیت انجام شد!')
                return redirect('home') # هدایت به صفحه اصلی

            except PhoneVerification.DoesNotExist:
                messages.error(request, 'کد وارد شده صحیح نمی‌باشد.')

    return render(request, 'users/verify_phone.html', {'phone_number': phone_number})
