from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        # Force English messages for account-related emails
        context['message'] = context.get('message', '').replace('سپاس‌گزاریم برای استفاده از', 'Thank you for using')
        context['message'] = context['message'].replace('\u200f', '')  # Remove RTL mark
        return super().send_mail(template_prefix, email, context)
