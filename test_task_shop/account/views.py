from typing import Union
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from .forms import UserRegisterForm


def register(request: HttpRequest) -> HttpResponse:
    """
    Handles the user registration process.

    If the request method is POST, it validates the user registration form.
    If the form is valid, creates a new inactive user and redirects to the login page.
    Otherwise, renders the registration form template.
    """
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]
            User.objects.create(
                username=username, email=email, password=password, is_active=False
            )
            messages.success(request, f"Account was created for {username}")
            return redirect("account:login")
    else:
        form = UserRegisterForm()
    return render(request, "account/registration/register.html", {"form": form})


def login_user(request: HttpRequest) -> HttpResponse:
    """
    Handles the user login process.

    If the user is authenticated, redirects to the dashboard. If the request method is POST,
    it authenticates the user. If authentication is successful, logs the user in and redirects
    to the dashboard; otherwise, shows an error message and redirects to the login page.
    """
    if request.user.is_authenticated:
        return redirect("account:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("account:dashboard")
        else:
            messages.info(request, "Username or Password is incorrect")
            return redirect("account:login")
    else:
        form = AuthenticationForm()
    return render(request, "account/login/login.html", {"form": form})


def logout_user(request: HttpRequest) -> HttpResponse:
    """
    Logs out the user and redirects to the products page.
    """
    logout(request)
    return redirect("shop:products")


@login_required(login_url="account:login")
def dashboard(request: HttpRequest) -> HttpResponse:
    """
    Renders the user dashboard.
    """
    return render(request, "account/dashboard/dashboard.html")


@login_required(login_url="account:login")
def delete_account(request: HttpRequest) -> Union[HttpResponse, HttpResponse]:
    """
    Deletes the authenticated user's account upon POST request.

    If the request method is POST, deletes the user account and redirects to the shop index page.
    Otherwise, redirects back to the profile page.
    """
    user = User.objects.get(id=request.user.id)
    if request.method == "POST":
        user.delete()
        return redirect("shop:index")
    return redirect("account:profile_user")
