import os
import secrets

from datetime import datetime, timezone

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

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
from museum_site.views import generic_template_page


def activate_account(request, token=None):
    data = {"title": "Activate Your Account"}

    if request.method == "POST":
        form = Activate_Account_Form(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            user.is_active = True
            user.profile.activation_token = ""
            user.profile.activation_time = None
            user.profile.save()
            user.save()

            # Check Patron status
            cron_path = os.path.join(SITE_ROOT, "cron")
            cron_log_path = os.path.join(SITE_ROOT, "log")
            cmd = "{}/patreon-scan.sh >> {}/cron.log".format(cron_path, cron_log_path)
            status = os.system(cmd)

            return redirect_with_querystring("login_user", "activation=1")

    else:
        form = Activate_Account_Form(initial={"activation_token": token})

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


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


def forgot_password(request):
    data = {"title": "Forgot Password"}

    if request.method == "POST":
        form = Forgot_Password_Form(request.POST)
        if form.is_valid():
            qs = User.objects.filter(email=form.cleaned_data["email"])
            if len(qs) == 1:  # Match found
                user = qs[0]
                token = secrets.token_urlsafe()
                user.profile.reset_token = token
                user.profile.reset_time = datetime.utcnow()
                user.profile.save()
                send_forgotten_password_email(user, request.META["HTTP_HOST"] + reverse("reset_password_with_token", args=[token]))
            return redirect("reset_password")
    else:
        form = Forgot_Password_Form()

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


def forgot_username(request):
    data = {"title": "Forgot Username"}

    if request.method == "POST":
        form = Forgot_Username_Form(request.POST)
        if form.is_valid():
            qs = User.objects.filter(email=form.cleaned_data["email"])
            if len(qs) == 1:  # Match found
                send_forgotten_username_email(qs[0])

            return render(request, "museum_site/user/forgot-username-complete.html", data)
    else:
        form = Forgot_Username_Form()

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


def login_user(request):
    data = {
        "title": "Account Login/Registration",
        "registration_open": ALLOW_REGISTRATION,
    }

    if request.POST.get("first_name"):  # Cheeky
        return redirect("index")

    if request.method == "POST" and request.POST.get("action") == "register":
        login_form = Login_Form()
        reg_form = User_Registration_Form(request.POST)
        if ALLOW_REGISTRATION and reg_form.is_valid():
            user = User.objects.create_user(
                reg_form.cleaned_data["requested_username"], reg_form.cleaned_data["requested_email"], reg_form.cleaned_data["password"]
            )
            user.is_active = False
            user.save()
            Profile.objects.create(user=user, patron_email=reg_form.cleaned_data["requested_email"])

            token = secrets.token_urlsafe()
            user.profile.accepted_tos = TERMS_DATE
            user.profile.activation_token = token
            user.profile.activation_time = datetime.now(timezone.utc)
            user.profile.save()

            send_account_verification_email(user, request.META["HTTP_HOST"] + reverse("activate_account_with_token", args=[token]))
            return redirect("activate_account")
    elif request.method == "POST" and request.POST.get("action") == "login":
        reg_form = User_Registration_Form()
        login_form = Login_Form(request.POST)
        if login_form.is_valid():
            user = authenticate(request, username=login_form.cleaned_data["username"], password=login_form.cleaned_data["password"])
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
                # Does the username exist?
                qs = User.objects.filter(username=login_form.cleaned_data["username"])
                if qs and not qs[0].is_active:
                    login_form.add_error(
                        "username",
                        mark_safe(
                            "This account has not been activated. Check the email address you signed up with for instructions on how to activate your "
                            "account.<br>"
                            "<a href='/user/resend-activation/'> Resend Activation Email</a>"
                        )
                    )
                else:
                    login_form.add_error("password", "Invalid credentials provided. Please double check your username and password and try again.")
    else:  # Unbound forms
        reg_form = User_Registration_Form()
        login_form = Login_Form()

    data["login_form"] = login_form
    data["reg_form"] = reg_form
    return render(request, "museum_site/user/login.html", data)


def logout_user(request):
    logout(request)
    return redirect("index")


def manage_saved_data(request):
    data = {
        "title": "Manage Saved Data",
        "pk": request.GET.get("pk"),
        "file": get_object_or_404(File, pk=request.GET.get("pk"))
    }

    if not request.GET.get("pk"):
        return redirect("index")
    return render(request, "museum_site/user/manage-saved-data.html", data)


def resend_account_activation(request):
    data = {
        "title": "Resend Account Activation Email",
        "errors": {
            "email": "",
            "etc": "",
        },
    }

    if request.method == "POST":
        form = Resent_Account_Activation_Email_Form(request.POST)
        if form.is_valid():
            qs = User.objects.filter(email=form.cleaned_data["email"])
            if len(qs) == 1:
                user = qs[0]
                if not user.is_active:
                    # Create token
                    token = secrets.token_urlsafe()
                    user.profile.activation_token = token
                    user.profile.activation_time = datetime.now(timezone.utc)
                    user.profile.save()
                    # Resend email
                    send_account_verification_email(user, request.META["HTTP_HOST"] + reverse("activate_account_with_token", args=[token]))
                    return redirect("activate_account")
    else:
        form = Resent_Account_Activation_Email_Form()

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


def reset_password(request, token=""):
    data = {"title": "Reset Password"}

    if request.method == "POST":
        form = Reset_Password_Form(request.POST)
        if form.is_valid():
            form.user.set_password(form.cleaned_data["new_password"])
            form.user.save()
            logout(request)
            return redirect_with_querystring("login_user", "password_reset=1")
    else:
        form = Reset_Password_Form(initial={"reset_token": token})

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


def update_tos(request):
    data = {
        "title": "Updated Terms of Service",
        "forced_logout": True
    }

    if request.method == "POST":
        form = Updated_Terms_Of_Service_Form(request.POST)
        if form.is_valid():
            request.user.profile.accepted_tos = TERMS_DATE
            request.user.profile.save()
            return redirect("my_profile")
    else:
        form = Updated_Terms_Of_Service_Form()

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


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
        "theme",
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

    if data["user_obj"].username:
        data["title"] = "Profile for " + data["user_obj"].username
        data["meta_context"] = {
            "author": ["name", data["user_obj"].username],
            "description": ["name", "User profile for {}".format(data["user_obj"].username)],
            "og:url": ["property", "https://museumofzzt.com" + data["user_obj"].profile.link()],
        }
    else:
        data["title"] = "Profile for Guest Visitor"
        data["meta_context"] = {
            "author": ["name", "Anonymous"],
            "description": ["name", "An overview of your Musuem of ZZT data"]
        }
    data["default_upload_cap"] = UPLOAD_CAP  # For guest users

    return render(request, "museum_site/user/profile.html", data)
