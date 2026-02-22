from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, PasswordChangeForm
from accounts.models import OTP
from .otp_utils import send_otp


def register_view(request):
    if request.user.is_authenticated:
        return redirect('content:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # inactive until OTP verified
            user.save()
            send_otp(user)
            request.session['otp_user_id'] = user.id
            messages.info(request, 'An OTP has been sent to your email.')
            return redirect('users:verify_otp')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('content:home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                send_otp(user)
                request.session['otp_user_id'] = user.id
                messages.info(request, 'An OTP has been sent to your email.')
                return redirect('users:verify_otp')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def verify_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('users:login')

    if request.method == 'POST':
        entered_code = request.POST.get('otp', '')
        try:
            user = User.objects.get(id=user_id)
            otp = OTP.objects.filter(user=user, code=entered_code, is_used=False).last()

            if otp and otp.is_valid():
                otp.is_used = True
                otp.save()

                if not user.is_active:
                    user.is_active = True
                    user.save()

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['otp_user_id']
                messages.success(request, f'Welcome, {user.name}!')
                return redirect('content:home')
            else:
                messages.error(request, 'Invalid or expired OTP. Try again.')

        except User.DoesNotExist:
            messages.error(request, 'Something went wrong.')

    return render(request, 'users/verify_otp.html')


def resend_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            send_otp(user)
            messages.success(request, 'A new OTP has been sent to your email.')
        except User.DoesNotExist:
            pass
    return redirect('users:verify_otp')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('content:home')


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('users:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


@login_required
def dashboard_view(request):
    from apps.content.models import Content
    from apps.playlists.models import Playlist
    recent_content = Content.objects.filter(
        uploaded_by=request.user
    ).order_by('-uploaded_at')[:5] if request.user.is_creator else []
    playlists = Playlist.objects.filter(user=request.user)[:5]
    context = {
        'recent_content': recent_content,
        'playlists': playlists,
    }
    return render(request, 'users/dashboard.html', context)
