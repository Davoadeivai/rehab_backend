from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm
from patients.sms_service import send_verification_code
from django.contrib.auth.models import User
from patients.models import Profile, PhoneVerification
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')

            # بررسی اینکه آیا کاربری با این شماره موبایل از قبل وجود دارد
            if Profile.objects.filter(phone_number=phone_number, phone_verified=True).exists():
                messages.error(request, 'کاربری با این شماره موبایل قبلا ثبت‌نام کرده است.')
                return render(request, 'users/register.html', {'form': form})

            # ذخیره اطلاعات کاربر در session برای استفاده بعد از تایید
            user_data = form.cleaned_data
            request.session['user_registration_data'] = {
                'username': user_data.get('username'),
                'password': form.cleaned_data.get('password2'), # UserCreationForm از password2 استفاده می‌کند
                'email': user_data.get('email'),
                'first_name': user_data.get('first_name'),
                'last_name': user_data.get('last_name'),
                'phone_number': phone_number,
            }

            # ارسال کد تایید
            success, message = send_verification_code(phone_number)

            if success:
                messages.info(request, f'کد تایید به شماره {phone_number} ارسال شد.')
                return redirect('verify_phone') # هدایت به صفحه تایید
            else:
                messages.error(request, message)
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

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
