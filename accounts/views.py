from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from .models import OTP
from .utils import send_otp

# --- REGISTER ---
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html')

        # Save user temporarily in session
        request.session['pending_user'] = {
            'username': username,
            'email': email,
            'password': password,
        }

        # Create a temporary user to send OTP (or use session email)
        # We create the user inactive until OTP verified
        user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
        send_otp(user)
        request.session['otp_user_id'] = user.id

        return redirect('verify_otp')

    return render(request, 'accounts/register.html')


# --- LOGIN ---
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            send_otp(user)
            request.session['otp_user_id'] = user.id
            return redirect('verify_otp')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


# --- VERIFY OTP ---
def verify_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('login')

    if request.method == 'POST':
        entered_code = request.POST['otp']

        try:
            user = User.objects.get(id=user_id)
            otp = OTP.objects.filter(user=user, code=entered_code, is_used=False).last()

            if otp and otp.is_valid():
                otp.is_used = True
                otp.save()

                # Activate user if registering
                if not user.is_active:
                    user.is_active = True
                    user.save()

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['otp_user_id']
                messages.success(request, 'Logged in successfully!')
                return redirect('dashboard')  # change to your home page
            else:
                messages.error(request, 'Invalid or expired OTP.')

        except User.DoesNotExist:
            messages.error(request, 'Something went wrong.')

    return render(request, 'accounts/verify_otp.html')


# --- RESEND OTP ---
def resend_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            send_otp(user)
            messages.success(request, 'A new OTP has been sent to your email.')
        except User.DoesNotExist:
            pass
    return redirect('verify_otp')