import secrets

from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.urls import reverse

from .common import *
from .constants import *
from .models import *
from .mail import (
    send_forgotten_username_email,
    send_forgotten_password_email,
    send_account_verification_email,
)


def activate_account(request, token=None):
    data = {
        "title": "Activate Your Account",
        "token": token,
        "resp": "WAITING"
    }

    if request.POST.get("action") == "activate-account":
        qs = User.objects.filter(
            profile__activation_token=request.POST.get("token")
        )
        if qs and len(qs) == 1:
            u = qs[0]
            u.is_active = True
            u.profile.activation_token = ""
            u.profile.activation_time = None
            u.profile.save()
            u.save()
            data["resp"] = "SUCCESS"
        else:
            data["resp"] = "FAILURE"

    return render(request, "museum_site/user-activate-account.html", data)


def forgot_password(request):
    data = {
        "title": "Forgot Password",
        "errors": {
            "email": "",
        }
    }

    if request.POST.get("action") == "forgot-password":
        email = request.POST.get("email")

        if not email:
            data["errors"]["email"] = "A valid email address was not provided."
            return render(
                request, "museum_site/user-forgot-password.html", data
            )

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
    data = {
        "title": "Forgot Username",
        "errors": {
            "email": "",
        }
    }

    if request.POST.get("action") == "forgot-username":
        email = request.POST.get("email")

        if not email:
            data["errors"]["email"] = "A valid email address was not provided."
            return render(
                request, "museum_site/user-forgot-username.html", data
            )

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
        "reg_errors": {
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
            data["errors"]["pwd"] = "Invalid credentials provided!"
    elif request.POST.get("action") == "register":
        if request.POST and ALLOW_REGISTRATION:
            create_account = True
            if request.POST.get("first-name"):  # Cheeky
                raise SuspiciousOperation("Invalid request")

            username = request.POST.get("reg-username")
            if not username:
                create_account = False
                data["reg_errors"]["username"] = ("A valid username was not "
                                                  "provided.")
            elif User.objects.filter(username=username).exists():
                create_account = False
                data["reg_errors"]["username"] = ("A user with this username "
                                                  "already exists.")

            # Check for unique email
            email = request.POST.get("reg-email")
            if not email:
                create_account = False
                data["reg_errors"]["email"] = ("A valid email address was not "
                                               "provided.")
            elif User.objects.filter(email=email).exists():
                create_account = False
                data["reg_errors"]["email"] = ("An account with this email "
                                               "address already exists.")

            # Check for matching passwords
            pwd = request.POST.get("reg-moz-pw")
            pwd_conf = request.POST.get("reg-moz-pw-conf")
            if pwd != pwd_conf:
                create_account = False
                data["reg_errors"]["pwd"] = ("Your password and password "
                                             "confirmation did not match.")
            elif not pwd or not pwd_conf:
                create_account = False
                data["reg_errors"]["pwd"] = "A valid password was not provided."

            # Check for TOS agreement
            tos = True if request.POST.get("tos-agreement") else False
            if not tos:
                create_account = False
                data["reg_errors"]["tos"] = ("You must agree to the terms of "
                                             "service to register.")

            # Create account
            if create_account:
                try:
                    user = User.objects.create_user(username, email, pwd)
                    user.is_active = False
                    user.save()
                    Profile.objects.create(user=user)
                    success = True
                except Exception:
                    success = False
                    data["reg_errors"]["etc"] = "Something went wrong when \
                    creating your account. Try again later and contact \
                    <a href='mailto:{}'>staff</a> if the problem \
                    persists.".format(EMAIL_ADDRESS)

                if success:
                    # Create a token to verify with
                    token = secrets.token_urlsafe()
                    user.profile.activation_token = token
                    user.profile.activation_time = datetime.now(timezone.utc)
                    user.profile.save()

                    # Email user verification link
                    send_account_verification_email(
                        user, request.META["HTTP_HOST"] + reverse(
                            "activate_account_with_token", args=[token]
                        )
                    )
                    return redirect("activate_account")

    return render(request, "museum_site/user-login.html", data)


def logout_user(request):
    logout(request)
    return redirect("index")


def resend_account_activation(request):
    data = {
        "title": "Resend Account Activation Email",
        "errors": {
            "email": "",
            "etc": "",
        },
    }

    if request.POST.get("action") == "resend-activation-email":
        success = True
        email = request.POST.get("email")

        if not email:
            data["errors"]["email"] = "A valid email address was not provided"
            success = False

        exists = User.objects.filter(email=email).exists()

        if not exists:
            data["errors"]["email"] = ("No account with that email address "
                                       "was found")
            success = False
        else:
            user = User.objects.get(email=email)
            if user.is_active:
                data["errors"]["etc"] = ("The account with that email address "
                                         "is already active.")
                success = False

            if success:
                # Create a token to verify with
                token = secrets.token_urlsafe()
                user.profile.activation_token = token
                user.profile.activation_time = datetime.now(timezone.utc)
                user.profile.save()

                # Email user verification link
                send_account_verification_email(
                    user, request.META["HTTP_HOST"] + reverse(
                        "activate_account_with_token", args=[token]
                    )
                )

                return redirect("activate_account")

    return render(
        request, "museum_site/user-resend-account-activation.html", data
    )


def reset_password(request, token=None):
    data = {
        "title": "Reset Password",
        "token": token,
        "errors": {
            "username": "",
            "pwd": "",
            "etc": "",
            "token": "",
        },
    }

    success = True

    if request.POST.get("action") == "reset-password":
        if token is None:
            token = request.POST.get("token")

        # Check that the token is valid
        exists = Profile.objects.filter(reset_token=token).exists()

        if token and exists:
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
            data["errors"]["token"] = ("Invalid password reset token.")
            success = False

        if success:
            u = User.objects.get(profile__reset_token=token)

            # Check that the token hasn't expired
            now = datetime.now(timezone.utc)
            print("NOW       ", now)
            print("RESET TIME", u.profile.reset_time)
            diff = now - u.profile.reset_time
            print("DIFF", diff)
            print("DIFF SEC", diff.seconds)
            if diff.seconds > TOKEN_EXPIRATION_SECS:
                data["errors"]["token"] = ("Your password reset token has "
                                           "expired. Please request another "
                                           "password reset.")
                success = False

            if success:
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
        if request.session.get(request.GET["delete"]):
            del request.session[request.GET["delete"]]

    data["user_data"] = []
    for k, v in request.session.items():
        if k not in excluded_keys:
            data["user_data"].append((k.replace("_", " ").title(), v))

    if request.user.is_authenticated:
        data["user_obj"] = request.user

    return render(request, "museum_site/user_profile.html", data)
