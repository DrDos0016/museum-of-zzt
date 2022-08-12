import secrets

from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.urls import reverse

from museum_site.common import *
from museum_site.constants import *
from museum_site.forms import *
from museum_site.models import *
from museum_site.mail import (
    send_forgotten_username_email,
    send_forgotten_password_email,
    send_account_verification_email,
)
from museum_site.private import BETA_USERNAME, BETA_PASSWORD


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

            # Check Patron status
            cron_path = os.path.join(SITE_ROOT, "cron")
            cron_log_path = os.path.join(SITE_ROOT, "log")
            cmd = "{}/patreon-scan.sh >> {}/cron.log".format(cron_path, cron_log_path)
            status = os.system(cmd)

            data["resp"] = "SUCCESS"
        else:
            data["resp"] = "FAILURE"

    return render(request, "museum_site/user/activate-account.html", data)


@login_required()
def change_password(request):
    data = {"title": "Change Password"}

    if request.method == "POST":
        form = Change_Password_Form(request.POST)
        form.db_password = request.user.password

        if form.is_valid():
            request.user.set_password(form.cleaned_data["new_password"])
            request.user.save()
            logout(request)
            return redirect("login_user")
    else:
        form = Change_Password_Form()

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


@login_required()
def change_char(request):
    data = {
        "title": "Change ASCII Char",
        "scripts": ["js/change-ascii-char.js"]
    }

    if request.method == "POST":
        form = Change_Ascii_Char_Form(request.POST)
    else:
        form = Change_Ascii_Char_Form(
            initial={"character": int(request.user.profile.char), "foreground": request.user.profile.fg, "background": request.user.profile.bg}
        )

    if form.is_valid():
        request.user.profile.char = form.cleaned_data["character"]
        request.user.profile.fg = form.cleaned_data["foreground"]
        request.user.profile.bg = form.cleaned_data["background"]
        request.user.profile.save()
        return redirect("my_profile")

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


@login_required()
def change_crediting_preferences(request):
    data = {"title": "Change Credit Preferences"}

    if request.method == "POST":
        form = Change_Crediting_Preferences_Form(request.POST)
        if form.is_valid():
            request.user.profile.site_credits_name = form.cleaned_data["site_credits_name"]
            request.user.profile.stream_credits_name = form.cleaned_data["stream_credits_name"]
            request.user.profile.save()
            return redirect("my_profile")
    else:
        form = Change_Crediting_Preferences_Form(
            initial={"site_credits_name": request.user.profile.site_credits_name, "stream_credits_name": request.user.profile.stream_credits_name}
        )

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


@login_required()
def change_email(request):
    data = {"title": "Change Email"}

    if request.method == "POST":
        form = Change_Email_Form(request.POST)
        form.db_password = request.user.password

        if form.is_valid():
            request.user.email = form.cleaned_data["new_email"]
            request.user.save()
            return redirect("my_profile")
    else:
        form = Change_Email_Form()

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


@login_required()
def change_patron_email(request):
    data = {"title": "Change Patron Email"}

    if request.method == "POST":
        form = Change_Patron_Email_Form(request.POST)
        if form.is_valid():
            request.user.profile.patron_email = form.cleaned_data["patron_email"]
            request.user.profile.save()
            return redirect("my_profile")
    else:
        form = Change_Patron_Email_Form()

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


@login_required()
def change_patronage_visibility(request):
    data = {"title": "Change Patronage Visibliity"}

    if request.method == "POST":
        form = Change_Patronage_Visibility_Form(request.POST)
        if form.is_valid():
            request.user.profile.patron_visibility = True if form.cleaned_data["visibility"] == "show" else False
            request.user.profile.save()
            return redirect("my_profile")
    else:
        form = Change_Patronage_Visibility_Form(initial={"visibility": ("show" if request.user.profile.patron_visibility else "hide")})

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


@login_required()
def change_pronouns(request):
    data = {
        "title": "Change Pronouns",
        "scripts": ["js/change-pronouns.js"]
    }

    if request.method == "POST":
        form = Change_Pronouns_Form(request.POST)
        if form.is_valid():
            pronouns = form.cleaned_data["pronouns"]
            if pronouns == "N/A":
                pronouns = ""
            elif pronouns == "CUSTOM":
                pronouns = form.cleaned_data["custom"]
            request.user.profile.pronouns = pronouns
            request.user.profile.save()
            return redirect("my_profile")
    else:
        current_pronoun_choice = request.user.profile.pronouns
        if current_pronoun_choice == "":
            current_pronoun_choice = "N/A"
        if current_pronoun_choice not in [i[0] for i in Change_Pronouns_Form.PRONOUN_CHOICES]:
            current_custom_choice = current_pronoun_choice
            current_pronoun_choice = "CUSTOM"
        else:
            current_custom_choice = ""
        form = Change_Pronouns_Form(initial={"pronouns": current_pronoun_choice, "custom": current_custom_choice})

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


@login_required()
def change_patron_perks(request):
    """ Generic function to handle poll nominations, stream selections, etc """
    data = {}
    reqs = {
        "/user/change-stream-poll-nominations/": {"form": Change_Patron_Stream_Poll_Nominations_Form, "field": "stream_poll_nominations"},
        "/user/change-stream-selections/": {"form": Change_Patron_Stream_Selections_Form, "field": "stream_selections"},
        "/user/change-closer-look-poll-nominations/": {"form": Change_Closer_Look_Poll_Nominations_Form, "field": "closer_look_nominations"},
        "/user/change-guest-stream-selections/": {"form": Change_Guest_Stream_Selections_Form, "field": "guest_stream_selections"},
        "/user/change-closer-look-selections/": {"form": Change_Closer_Look_Selections_Form, "field": "closer_look_selections"},
        "/user/change-bkzzt-topics/": {"form": Change_Bkzzt_Topics_Form, "field": "bkzzt_topics"},
    }

    if request.method == "POST":
        form = reqs[request.path]["form"](request.POST)
        field = reqs[request.path]["field"]
        if form.is_valid():
            setattr(request.user.profile, field, form.cleaned_data[field])
            request.user.profile.save()
            return redirect("my_profile")
    else:
        initial_value = getattr(request.user.profile, reqs[request.path]["field"])
        form = reqs[request.path]["form"](initial={reqs[request.path]["field"]: initial_value})

    data["title"] = form.heading
    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


@login_required()
def change_username(request):
    data = {
        "title": "Change Username",
        "errors": {},
        "changed": False
    }

    if request.method == "POST":
        form = Change_Username_Form(request.POST)
        form.db_password = request.user.password
    else:
        form = Change_Username_Form()

    if form.is_valid():
        # Change a user's username and update author for their reviews
        request.user.username = form.cleaned_data["new_username"]
        request.user.save()

        # Update author field on this user's reviews
        updated = Review.objects.filter(user_id=request.user.id).update(author=form.cleaned_data["new_username"])

        # Log out and redirect to login page
        logout(request)
        return redirect("login_user")

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


def error_login(request):
    data = {"title": "Access Restricted"}
    data["now"] = datetime.now()
    return render(request, "museum_site/user/error-login.html", data)


def error_registration(request):
    data = {"title": "Access Restricted"}
    data["now"] = datetime.now()
    return render(request, "museum_site/user/error-registration.html", data)


def error_password_reset(request):
    data = {"title": "Access Restricted"}
    data["now"] = datetime.now()
    return render(request, "museum_site/user/error-password-reset.html", data)


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
                request, "museum_site/user/forgot-password.html", data
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

    return render(request, "museum_site/user/forgot-password.html", data)


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
                request, "museum_site/user/forgot-username.html", data
            )

        # Check that the email is even in use
        exists = User.objects.filter(email=email).exists()
        if exists:
            u = User.objects.get(email=email)
            send_forgotten_username_email(u)

        return render(
            request,
            "museum_site/user/forgot-username-complete.html",
            data
        )

    return render(request, "museum_site/user/forgot-username.html", data)


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

            # Check for a newer TOS
            if TERMS_DATE > user.profile.accepted_tos:
                return redirect("update_tos")

            if request.GET.get("next"):
                return redirect(request.GET["next"])
            else:
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
            else:
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
                    Profile.objects.create(user=user, patron_email=email)
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
                    user.profile.accepted_tos = TERMS_DATE
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

    return render(request, "museum_site/user/login.html", data)


def logout_user(request):
    logout(request)
    return redirect("index")


def manage_saved_data(request):
    data = {
        "title": "Manage Saved Data",
        "pk": request.GET.get("pk"),
        "file": File.objects.filter(pk=request.GET.get("pk")).first()
    }
    return render(request, "museum_site/user/manage-saved-data.html", data)


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
        request, "museum_site/user/resend-account-activation.html", data
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

    return render(request, "museum_site/user/reset-password.html", data)


def update_tos(request):
    data = {
        "title": "Updated Terms of Service",
        "terms": TERMS,
        "reg_errors": {}
    }

    if request.POST.get("action") == "update-tos":
        if not request.POST.get("tos-agreement"):
            data["reg_errors"]["tos"] = ("You must accept the latest terms to "
                                         "continue using your account.")
        else:
            request.user.profile.accepted_tos = TERMS_DATE
            request.user.profile.save()
            return redirect("my_profile")

    return render(request, "museum_site/user/update-tos.html", data)


def user_profile(request, user_id=None, **kwargs):
    data = {
        "title": "",
        "BETA_USERNAME": BETA_USERNAME,
        "BETA_PASSWORD": BETA_PASSWORD,
    }
    excluded_keys = [
        "_auth_user_id",
        "_auth_user_backend",
        "_auth_user_hash",
        "login_attempts",
        "lockout_expiration",
        "reg_attempts",
        "pw_reset_attempts",
    ]

    data["TIERS"] = {
        "CHAR_2": TIER_CHAR_2,
        "PURPLE_KEYS": TIER_5_PURPLE_KEYS,
        "ZZT_RIVER": TIER_ZZT_RIVER,
        "BOARD_SIZE": TIER_BOARD_SIZE,
        "THROWSTAR_SEEK": TIER_THROWSTAR_SEEK,
        "HEALTH": TIER_HEALTH,
        "BRIBE_THE_MAYOR": TIER_BRIBE_THE_MAYOR
    }

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
        data["user_obj"] = request.user
        if request.user.is_authenticated:
            data["private"] = True
        else:
            data["show_session"] = True
            data["guest"] = True
    else:
        data["show_session"] = False
        user_id = int(user_id)
        data["user_obj"] = get_object_or_404(User, pk=user_id)
        if user_id == request.user.id:
            data["private"] = True
            data["show_session"] = True

    # Overrides
    if request.user.is_staff:
        data["private"] = True
    if request.GET.get("public"):
        data["private"] = False

    # Check Patreon Status
    if data["private"] and request.GET.get("check_patronage"):
        cron_path = os.path.join(SITE_ROOT, "cron")
        cron_log_path = os.path.join(SITE_ROOT, "log")
        cmd = "{}/patreon-scan.sh >> {}/cron.log".format(cron_path, cron_log_path)
        status = os.system(cmd)

    data["title"] = "Profile for " + data["user_obj"].username
    return render(request, "museum_site/user/profile.html", data)
