from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, label="شماره موبایل", help_text="مثال: 09123456789")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('phone_number', 'email', 'first_name', 'last_name',)
