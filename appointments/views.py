from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def calendar_view(request):
    """نمایش تقویم نوبت‌دهی"""
    return render(request, 'appointments/calendar.html') 