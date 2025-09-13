from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        print("Form data:", request.POST)  # Debug
        print("Form errors:", form.errors)  # Debug
        
        if form.is_valid():
            try:
                user = form.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 'ثبت نام شما با موفقیت انجام شد.')
                logging.getLogger('user.activity').info(f"User registered: {user.username} ({user.email}) from IP {request.META.get('REMOTE_ADDR')}")
                return redirect('home')
            except Exception as e:
                print("Error during user creation:", str(e))  # Debug
                messages.error(request, f'خطا در ثبت نام: {str(e)}')
        else:
            # Log form errors for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"{field}: {error}")
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})

@csrf_exempt
def custom_logout(request):
    if request.method in ['GET', 'POST']:
        logout(request)
        return redirect('login')
    return HttpResponse("Method not allowed", status=405)
