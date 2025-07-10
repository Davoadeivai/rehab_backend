from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class CustomUserCreationForm(UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'captcha')

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
