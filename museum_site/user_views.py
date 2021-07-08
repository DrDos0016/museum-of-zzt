import secrets

from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
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


def change_password(request):
    data = {
        "title": "Change Password",
        "errors": {
        },
        "changed": False
    }

    success = True
    if request.POST.get("action") == "change-password":
        # Check current password
        cur = request.POST.get("moz-pwd-cur")
        if not cur:
            success = False
            data["errors"]["cur_pwd"] = ("You must authenticate this action "
                                         "by providing your current password.")

        # Check current password matches
        if not check_password(cur, request.user.password):
            success = False
            data["errors"]["cur_pwd"] = "Invalid credentials provided!"

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
        elif len(pwd) < MIN_PASSWORD_LENGTH:
            success = False
            data["errors"]["pwd"] = ("Your password must be at least eight "
                                     "characters in length.")

        # Change the password
        if success:
            request.user.set_password(pwd)
            request.user.save()
            logout(request)
            data["changed"] = True

    return render(request, "museum_site/user-change-password.html", data)


def change_char(request):
    data = {
        "title": "Change ASCII Char",
        "errors": {
        },
        "changed": False
    }

    data["char_list"] = list(range(0, 256))
    data["characters"] = ASCII_UNICODE_CHARS
    data["colors"] = [
        "black", "blue", "green", "cyan", "red", "purple", "yellow", "white",
        "darkgray", "darkblue", "darkgreen", "darkcyan", "darkred",
        "darkpurple", "darkyellow", "gray"
    ]

    success = True
    if request.POST.get("action") == "change-ascii-char":
        character = request.POST.get("character")
        fg = request.POST.get("foreground")
        bg = request.POST.get("background")

        try:
            character = int(character)
        except ValueError:
            data["error"] = ("Something went wrong. Your ASCII character was "
                             "not updated.")
            success = False

        # Override invalid values
        if character < 0 or character > 255:
            character = 2
        if fg not in data["colors"]:
            fg = "white"
        if bg not in data["colors"] and bg != "transparent":
            bg = "darkblue"

        if success:
            request.user.profile.char = character
            request.user.profile.fg = fg
            request.user.profile.bg = bg

            try:
                request.user.profile.save()
                return redirect("my_profile")
            except Exception:
                data["error"] = ("Something went wrong. Your ASCII character "
                                 "was not updated.")

    return render(request, "museum_site/user-change-ascii-char.html", data)


def change_credit_preferences(request):
    data = {
        "title": "Change Credit Preferences",
        "errors": {
        },
        "changed": False,
    }

    success = True
    if request.POST.get("action") == "change-credit-preferences":

        site_credits = request.POST.get("site-credits", "")
        stream_credits = request.POST.get("stream-credits", "")

        request.user.profile.site_credits_name = site_credits
        request.user.profile.stream_credits_name = stream_credits

        try:
            request.user.profile.save()
            return redirect("my_profile")
        except Exception:
            data["error"] = ("Something went wrong. Your crediting "
                             "preferences were not updated.")

    return render(
        request, "museum_site/user-change-credit-preferences.html", data
    )


def change_email(request):
    data = {
        "title": "Change Email",
        "errors": {
        },
        "changed": False
    }

    success = True
    if request.POST.get("action") == "change-email":
        # Check current password
        cur = request.POST.get("moz-pwd-cur")
        if not cur:
            success = False
            data["errors"]["cur_pwd"] = ("You must authenticate this action "
                                         "by providing your current password.")

        # Check current password matches
        if not check_password(cur, request.user.password):
            success = False
            data["errors"]["cur_pwd"] = "Invalid credentials provided!"

        # Check for matching emails
        email = request.POST.get("email")
        email_conf = request.POST.get("conf-email")
        if email != email_conf:
            success = False
            data["errors"]["email"] = ("Your email address and email address "
                                       "confirmation did not match.")

        # Check for blank
        if email == "":
            success = False
            data["errors"]["email"] = "A valid email address was not provided."

        # Check email availability
        if User.objects.filter(username__iexact=email).exists():
            success = False
            data["errors"]["email"] = "Requested email address is unavailable."

        # Change the email address
        if success:
            request.user.email = email
            request.user.save()
            return redirect("my_profile")

    return render(request, "museum_site/user-change-email.html", data)


def change_patronage_visibility(request):
    data = {
        "title": "Change Patronage Visibliity",
        "errors": {
        },
        "changed": False
    }

    success = True
    if request.POST.get("action") == "change-patronage-visibility":

        visibility = True if request.POST.get("visibility") == "on" else False

        request.user.profile.patron_visibility = visibility

        try:
            request.user.profile.save()
            return redirect("my_profile")
        except Exception:
            data["error"] = ("Something went wrong. Your patronage visibility "
                             "was not updated.")

    return render(
        request, "museum_site/user-change-patronage-visibility.html", data
    )


def change_pronouns(request):
    data = {
        "title": "Change Pronouns",
        "errors": {
        },
        "changed": False,
        "common_pronouns": ["", "He/Him", "It/Its", "She/Her", "They/Them"],
    }

    success = True
    if request.POST.get("action") == "change-pronouns":

        pronouns = request.POST.get("pronouns", "")
        if pronouns == "CUSTOM":
            pronouns = request.POST.get("custom", "")

        request.user.profile.pronouns = pronouns

        try:
            request.user.profile.save()
            return redirect("my_profile")
        except Exception:
            data["error"] = ("Something went wrong. Your pronouns were not "
                             "updated.")

    return render(request, "museum_site/user-change-pronouns.html", data)


def change_username(request):
    data = {
        "title": "Change Username",
        "errors": {
        },
        "changed": False
    }

    success = True
    if request.POST.get("action") == "change-username":
        # Check current password
        cur = request.POST.get("moz-pwd-cur")
        if not cur:
            success = False
            data["errors"]["cur_pwd"] = ("You must authenticate this action "
                                         "by providing your current password.")

        # Check current password matches
        if not check_password(cur, request.user.password):
            success = False
            data["errors"]["cur_pwd"] = "Invalid credentials provided!"

        # Check for matching usernames
        uname = request.POST.get("username")
        uname_conf = request.POST.get("conf-username")
        if uname != uname_conf:
            success = False
            data["errors"]["username"] = ("Your username and username "
                                          "confirmation did not match.")

        # Check for blank
        if uname == "":
            success = False
            data["errors"]["username"] = "A valid username was not provided."

        # Check username availability
        if User.objects.filter(username__iexact=uname).exists():
            success = False
            data["errors"]["username"] = "Requested username is unavailable."

        # Change the password
        if success:
            request.user.username = uname
            request.user.save()
            logout(request)
            return redirect("login_user")

    return render(request, "museum_site/user-change-username.html", data)


def error_login(request):
    data = {"title": "Access Restricted"}
    data["now"] = datetime.now()
    return render(request, "museum_site/user-error-login.html", data)


def error_registration(request):
    data = {"title": "Access Restricted"}
    data["now"] = datetime.now()
    return render(request, "museum_site/user-error-registration.html", data)


def error_password_reset(request):
    data = {"title": "Access Restricted"}
    data["now"] = datetime.now()
    return render(request, "museum_site/user-error-password-reset.html", data)


def forgot_password(request):
    data = {
        "title": "Forgot Password",
        "errors": {
            "email": "",
        }
    }

    if request.POST.get("action") == "forgot-password":

        if not (throttle_check(
            request, "pw_reset_attempts", "pw_reset_expiration",
            MAX_PASSWORD_RESETS, lockout_mins=60
        )):
            return redirect("error_password_reset")

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
        if not (throttle_check(
            request, "login_attempts", "lockout_expiration",
            MAX_LOGIN_ATTEMPTS,
        )):
            return redirect("error_login")

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
            # Reset login attempts
            del request.session["login_attempts"]
            del request.session["lockout_expiration"]
            return redirect("my_profile")
        else:
            # Does the usename exist?
            qs = User.objects.filter(username=acct)
            if qs and not qs[0].is_active:
                data["errors"]["username"] = (
                    "This account has not been activated. Check the email "
                    "address you signed up with for instructions on how to "
                    "activate your account. "
                    "<a href='/user/resend-activation/'>"
                    "Resend Activation Email</a>"
                )

            data["errors"]["pwd"] = "Invalid credentials provided!"

    elif request.POST.get("action") == "register":
        if ALLOW_REGISTRATION:
            if not (throttle_check(
                request, "reg_attempts", "reg_expiration",
                MAX_REGISTRATION_ATTEMPTS,
            )):
                return redirect("error_registration")

            create_account = True
            if request.POST.get("first-name"):  # Cheeky
                raise SuspiciousOperation("Invalid request")

            username = request.POST.get("reg_username")
            if not username:
                create_account = False
                data["reg_errors"]["username"] = ("A valid username was not "
                                                  "provided.")
            elif User.objects.filter(username=username).exists():
                create_account = False
                data["reg_errors"]["username"] = ("A user with this username "
                                                  "already exists.")

            # Check for unique email
            email = request.POST.get("reg_email")
            if not email:
                create_account = False
                data["reg_errors"]["email"] = ("A valid email address was not "
                                               "provided.")
            elif User.objects.filter(email=email).exists():
                create_account = False
                data["reg_errors"]["email"] = ("An account with this email "
                                               "address already exists.")

            # Check for matching passwords of minimum length
            pwd = request.POST.get("reg_moz-pw")
            pwd_conf = request.POST.get("reg_moz-pw-conf")
            if pwd != pwd_conf:
                create_account = False
                data["reg_errors"]["pwd"] = ("Your password and password "
                                             "confirmation did not match.")
            elif not pwd or not pwd_conf:
                create_account = False
                data["reg_errors"]["pwd"] = "A valid password was not provided."
            elif len(pwd) < MIN_PASSWORD_LENGTH:
                create_account = False
                data["reg_errors"]["pwd"] = ("Your password must be at least "
                                             "eight characters in length.")

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
            data["errors"]["email"] = ("No inactive account with that email "
                                       "address was found")
            success = False
        else:
            user = User.objects.get(email=email)
            if user.is_active:
                data["errors"]["email"] = ("No inactive account with that "
                                           "email address was found")
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
            elif len(pwd) < MIN_PASSWORD_LENGTH:
                success = False
                data["errors"]["pwd"] = ("Your password must be at least "
                                         "eight characters in length.")

        else:
            data["errors"]["token"] = ("Invalid password reset token.")
            success = False

        if success:
            u = User.objects.get(profile__reset_token=token)

            # Check that the token hasn't expired
            now = datetime.now(timezone.utc)
            diff = now - u.profile.reset_time
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


def user_profile(request, user_id=None):
    data = {"title": "User Profile"}
    excluded_keys = [
        "_auth_user_id",
        "_auth_user_backend",
        "_auth_user_hash",
        "login_attempts",
        "lockout_expiration",
    ]

    to_delete = request.GET.get("delete")
    if to_delete and to_delete not in excluded_keys:
        if request.session.get(request.GET["delete"]):
            del request.session[request.GET["delete"]]

    data["user_data"] = []
    data["show_session"] = True
    for k, v in request.session.items():
        if k not in excluded_keys:
            data["user_data"].append((k, v, k.replace("_", " ").title()))

    # Find the user
    data["private"] = False
    if user_id is None:
        if request.user.is_authenticated:
            data["user_obj"] = request.user
            data["private"] = True
    else:
        data["show_session"] = False
        user_id = int(user_id)
        data["user_obj"] = get_object_or_404(User, pk=user_id)
        if user_id == request.user.id:
            data["private"] = True
            data["show_session"] = True

    # Overrides
    if request.GET.get("public"):
        data["private"] = False

    return render(request, "museum_site/user-profile.html", data)
