from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from captcha.fields import CaptchaField

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label='نام', max_length=30, required=True)
    last_name = forms.CharField(label='نام خانوادگی', max_length=30, required=True)
    captcha = CaptchaField()
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=\[\]{}|;:,.<>?~`-]+$', username):
            raise ValidationError('نام کاربری فقط می‌تواند شامل حروف انگلیسی، اعداد و کاراکترهای بالای کیبورد باشد.')
        if len(username) < 4 or len(username) > 30:
            raise ValidationError('نام کاربری باید بین ۴ تا ۳۰ کاراکتر باشد.')
        return username

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=\[\]{}|;:,.<>?~`-]+$', first_name):
            raise ValidationError('نام فقط می‌تواند شامل حروف انگلیسی، اعداد و کاراکترهای بالای کیبورد باشد.')
        if first_name and len(first_name) > 30:
            raise ValidationError('نام نباید بیش از ۳۰ کاراکتر باشد.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=\[\]{}|;:,.<>?~`-]+$', last_name):
            raise ValidationError('نام خانوادگی فقط می‌تواند شامل حروف انگلیسی، اعداد و کاراکترهای بالای کیبورد باشد.')
        if last_name and len(last_name) > 30:
            raise ValidationError('نام خانوادگی نباید بیش از ۳۰ کاراکتر باشد.')
        return last_name

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        import re
        if not re.match(r'^[A-Za-z0-9!@#$%^&*()_+=\[\]{}|;:,.<>?~`-]+$', password1):
            raise ValidationError('رمز عبور فقط می‌تواند شامل حروف انگلیسی، اعداد و کاراکترهای بالای کیبورد باشد.')
        if len(password1) < 8 or len(password1) > 30:
            raise ValidationError('رمز عبور باید بین ۸ تا ۳۰ کاراکتر باشد.')
        return password1
        
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        
        if not email:
            raise ValidationError('لطفا یک آدرس ایمیل معتبر وارد کنید.')
            
        # Check for common typos in email domains
        common_typos = {
            'gmail.coom': 'gmail.com',
            'gmail.con': 'gmail.com',
            'gmail.cm': 'gmail.com',
            'gmail.c': 'gmail.com',
            'gmai.com': 'gmail.com',
            'gmal.com': 'gmail.com',
            'gmaill.com': 'gmail.com',
            'yaho.com': 'yahoo.com',
            'yaho.co': 'yahoo.com',
            'yahu.com': 'yahoo.com',
            'yahooo.com': 'yahoo.com',
            'outlok.com': 'outlook.com',
            'hotmail.co': 'hotmail.com',
            'hotmail.con': 'hotmail.com',
            'hotmail.cm': 'hotmail.com',
            'yahoo.co': 'yahoo.com',
            'yandex.ru': 'yandex.com',
            'yandex.com': 'yandex.com',
            'mail.ru': 'mail.ru',
            'gmx.de': 'gmx.net',
            'gmx.com': 'gmx.net',
            'gmx.at': 'gmx.net'
        }
        
        # Split email into local and domain parts
        if '@' in email:
            local_part, domain = email.rsplit('@', 1)
            domain = domain.lower()
            
            # Check for common typos and suggest correction
            if domain in common_typos:
                correct_domain = common_typos[domain]
                if domain != correct_domain:
                    self.cleaned_data['email'] = f"{local_part}@{correct_domain}"
                    return self.cleaned_data['email']
        
        # More permissive email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError('لطفا یک آدرس ایمیل معتبر وارد کنید. مثال: example@domain.com')
            
        # Check if email already exists
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('این آدرس ایمیل قبلاً ثبت‌نام کرده‌است. لطفاً وارد شوید یا از گزینه فراموشی رمز عبور استفاده کنید.')
            
        return email
