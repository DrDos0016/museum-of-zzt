import secrets

from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse

from .common import *
from .constants import *
from .models import *
from .mail import send_forgotten_username_email, send_forgotten_password_email


def forgot_password(request):
    data = {"title": "Forgot Password"}

    if request.POST.get("action") == "forgot-password":
        email = request.POST.get("email")
        # Check that the email is even in use
        exists = User.objects.filter(email=email).exists()
        if exists:
            u = User.objects.get(email=email)
            token = secrets.token_urlsafe()
            u.profile.reset_token = token
            u.profile.reset_time = datetime.utcnow()
            u.profile.save()
            send_forgotten_password_email(
                u, request.META["HTTP_HOST"] + reverse(
                    "reset_password_with_token", args=[token]
                )
            )

        return redirect("reset_password")

    return render(request, "museum_site/user-forgot-password.html", data)


def forgot_username(request):
    data = {"title": "Forgot Username"}

    if request.POST.get("action") == "forgot-username":
        email = request.POST.get("email")
        # Check that the email is even in use
        exists = User.objects.filter(email=email).exists()
        if exists:
            u = User.objects.get(email=email)
            send_forgotten_username_email(u)

        return render(
            request,
            "museum_site/user-forgot-username-complete.html",
            data
        )

    return render(request, "museum_site/user-forgot-username.html", data)


def login_user(request):
    data = {
        "title": "Account Login/Registration",
        "errors": {
            "username": "",
            "pwd": "",
            "etc": "",
        },
        "registration_open": ALLOW_REGISTRATION,
        "terms": TERMS,
    }

    if request.POST.get("action") == "login":
        acct = request.POST.get("username")
        pwd = request.POST.get("moz-pw")

        if not acct:
            data["errors"]["username"] = "A valid username was not provided."

        if not pwd:
            data["errors"]["pwd"] = "A valid password was not provided."

        # Try username authentication
        user = authenticate(request, username=acct, password=pwd)

        if user is not None:
            # Create a Profile if they do not have one
            if not hasattr(user, "profile"):
                Profile.objects.create(user=user)

            login(request, user)
            return redirect("user_profile")
        else:
            data["errors"]["etc"] = "Invalid credentials provided!"
    elif request.POST.get("action") == "register":
        if request.POST and ALLOW_REGISTRATION:
            create_account = True
            if request.POST.get("first-name"):  # Cheeky
                raise SuspiciousOperation("Invalid request")

            username = request.POST.get("reg-username")
            if not username:
                create_account = False
                data["errors"]["username"] = ("A valid username was not "
                                              "provided.")
            elif User.objects.filter(username=username).exists():
                create_account = False
                data["errors"]["username"] = ("A user with this username "
                                              "already exists.")

            # Check for unique email
            email = request.POST.get("reg-email")
            if not email:
                create_account = False
                data["errors"]["email"] = ("A valid email address was not "
                                           "provided.")
            elif User.objects.filter(email=email).exists():
                create_account = False
                data["errors"]["email"] = ("An account with this email "
                                           "address already exists.")

            # Check for matching passwords
            pwd = request.POST.get("reg-moz-pw")
            pwd_conf = request.POST.get("reg-moz-pw-conf")
            if pwd != pwd_conf:
                create_account = False
                data["errors"]["pwd"] = ("Your password and password "
                                         "confirmation did not match.")
            elif not pwd or not pwd_conf:
                create_account = False
                data["errors"]["pwd"] = "A valid password was not provided."

            # Check for TOS agreement
            tos = True if request.POST.get("tos-agreement") else False
            if not tos:
                create_account = False
                data["errors"]["tos"] = ("You must agree to the terms of "
                                         "service to register.")

            # Create account
            if create_account:
                try:
                    user = User.objects.create_user(username, email, pwd)
                    Profile.objects.create(user=user)
                    data["errors"]["etc"] = "Account created successfully!"
                    return redirect("registration_complete")
                except Exception:
                    data["errors"]["etc"] = "Something went wrong when \
                    creating your account. Try again later and contact \
                    <a href='mailto:{}'>staff</a> if the problem \
                    persists.".format(EMAIL_ADDRESS)

    return render(request, "museum_site/user-login.html", data)


def logout_user(request):
    logout(request)
    return redirect("index")


def reset_password(request, token=None):
    data = {
        "title": "Reset Password",
        "token": token,
        "errors": {
            "username": "",
            "pwd": "",
            "etc": "",
            },
        }

    success = True
    if request.POST.get("action") == "reset-password":
        # Check that the token is valid
        exists = Profile.objects.filter(reset_token=token).exists()

        if exists:
            # Check for matching passwords
            pwd = request.POST.get("moz-pw")
            pwd_conf = request.POST.get("moz-pw-conf")
            if pwd != pwd_conf:
                success = False
                data["errors"]["pwd"] = ("Your password and password "
                                         "confirmation did not match.")
            elif not pwd or not pwd_conf:
                success = False
                data["errors"]["pwd"] = "A valid password was not provided."

        else:
            print("Exists was false")

        if success:
            u = User.objects.get(profile__reset_token=token)
            # Update the password
            u.set_password(pwd)
            u.save()
            return redirect("reset_password_complete")

    return render(request, "museum_site/user-reset-password.html", data)


def user_profile(request):
    data = {"title": "User Profile"}
    excluded_keys = [
        "_auth_user_id",
        "_auth_user_backend",
        "_auth_user_hash",
    ]

    to_delete = request.GET.get("delete")
    if to_delete and to_delete not in excluded_keys:
        del request.session[request.GET["delete"]]

    data["user_data"] = []
    for k, v in request.session.items():
        if k not in excluded_keys:
            data["user_data"].append((k, v))

    if request.user.is_authenticated:
        data["user_obj"] = request.user

    return render(request, "museum_site/user_profile.html", data)
