from account.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            User.objects.create(username=username, email=email, password=password, is_active=False)
            messages.success(request, 'Account was created for ' + username)
            return redirect('account:login')
    else:
        form = UserRegisterForm()
    return render(request, 'account/registration/register.html', {'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('account:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('account:dashboard')
        else:
            messages.info(request, 'Username or Password is incorrect')
            return redirect('account:login')
    else:
        form = AuthenticationForm()
    return render(request, 'account/login/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('shop:products')


@login_required(login_url='account:login')
def dashboard(request):
    return render(request, 'account/dashboard/dashboard.html')


@login_required(login_url='account:login')
def delete_account(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        user.delete()
        return redirect('shop:index')
    return redirect(request, 'account/dashboard/profile_user.html')
