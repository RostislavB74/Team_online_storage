import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, OTP
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                otp_code = ''.join(random.choices('0123456789', k=6))
                OTP.objects.create(
                    user=user,
                    code=otp_code,
                    expires_at=timezone.now() + timedelta(minutes=5)
                )
                print(f"OTP for {username}: {otp_code}")
                request.session['otp_user_id'] = user.id
                return redirect('verify_otp')
            else:
                messages.error(request, 'Невірний логін або пароль.')
        else:
            messages.error(request, 'Невірний логін або пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Реєстрація успішна! Увійдіть, щоб продовжити.')
            return redirect('login')
        else:
            messages.error(request, 'Помилка реєстрації. Перевірте форму.')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        user_id = request.session.get('otp_user_id')
        if user_id:
            user = User.objects.get(id=user_id)
            otp = OTP.objects.filter(
                user=user,
                code=otp_code,
                expires_at__gte=timezone.now()
            ).first()
            if otp:
                login(request, user)
                otp.delete()
                messages.success(request, f'Вітаємо, {user.username}!')
                del request.session['otp_user_id']
                return redirect('profile')
            else:
                messages.error(request, 'Невірний або прострочений OTP.')
        else:
            messages.error(request, 'Сесія недійсна. Спробуйте увійти знову.')
    return render(request, 'users/verify_otp.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Ви вийшли з системи.')
    return redirect('login')

@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, 'users/profile.html', {'profile': profile})

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })