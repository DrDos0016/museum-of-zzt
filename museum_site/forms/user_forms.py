from datetime import datetime, timedelta, timezone

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

from museum_site.constants import EMAIL_ADDRESS, TERMS
from museum_site.fields import Faux_Field, Museum_Color_Choice_Field, Museum_Choice_Field, Museum_TOS_Field
from museum_site.widgets import Ascii_Character_Widget, Ascii_Color_Widget, Faux_Widget, Terms_Of_Service_Widget

PASSWORD_HELP_TEXT = "Use a unique password for your account with a minimum length of <b>8</b> characters. Passwords are hashed and cannot be viewed by staff."


class Activate_Account_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Activate Account"
    heading = "Activate Account"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Your account has been created, but is currently <b>INACTIVE</b>.</p>"
        "<p>Please wait a moment and then check your inbox for an email containing a link to verify your account. "
        "If you haven't received one, check your spam folder as well. "
        "If you still haven't received a verification message <a href='mailto:{}'> contact Dr. Dos</a> for manual activation.</p>"
        "<p><a href='/user/resend-activation'>Resend activation email</a>.</p>".format(EMAIL_ADDRESS)
    )

    activation_token = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()

        qs = User.objects.filter(profile__activation_token=cleaned_data.get("activation_token"))

        if len(qs) != 1:
            self.add_error("activation_token", "A user account with the provided token was not found")
        else:
            cleaned_data["user"] = qs.first()
        return cleaned_data

class Change_Ascii_Char_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change ASCII Character"
    heading = "Change ASCII Character"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Choose an ASCII representation for yourself. This character will be displayed alongside your username whenever it is used throughout the site.</p>"
    )
    COLOR_CHOICES = (
        ("black", "Black"),
        ("blue", "Blue"),
        ("green", "Green"),
        ("cyan", "Cyan"),
        ("red", "Red"),
        ("purple", "Purple"),
        ("yellow", "Yellow"),
        ("white", "White"),
        ("darkgray", "Dark Gray"),
        ("darkblue", "Dark Blue"),
        ("darkgreen", "Dark Green"),
        ("darkcyan", "Dark Cyan"),
        ("darkred", "Dark Red"),
        ("darkpurple", "Dark Purple"),
        ("darkyellow", "Dark Yellow"),
        ("gray", "Gray")
    )

    character = forms.IntegerField(
        min_value=0,
        max_value=255,
        widget=Ascii_Character_Widget(),
        help_text="Click on an ASCII character in the table to select it",
    )
    foreground = Museum_Color_Choice_Field(choices=COLOR_CHOICES, widget=Ascii_Color_Widget(choices=COLOR_CHOICES))
    background = Museum_Color_Choice_Field(choices=COLOR_CHOICES, widget=Ascii_Color_Widget(choices=COLOR_CHOICES, allow_transparent=True))
    preview = Faux_Field(label="Preview", widget=Faux_Widget("museum_site/widgets/ascii-preview-widget.html"), required=False)


class Change_Email_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Email Address"
    heading = "Change Email Address"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>You may change your account's email address here. This address will be used to help you recover your account in the event your forget your "
        "username or password, so keep it up to date!</p>")

    current_password = forms.CharField(widget=forms.PasswordInput())
    new_email = forms.EmailField()
    confirm_email = forms.EmailField()

    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get("new_email", "")

        # Check requested email and confirmation match
        if new_email != cleaned_data.get("confirm_email", ""):
            self.add_error("confirm_email", "Email confirmation must match newly provided email address")

        # Check availability
        if User.objects.filter(email=new_email).exists():
            self.add_error("new_email", "Requested email address is unavailable.")

        # Check current password
        if not check_password(cleaned_data.get("current_password"), self.db_password):
            self.add_error("current_password", "Invalid password")


class Change_Password_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Password"
    heading = "Change Password"
    attrs = {"method": "POST"}
    text_prefix = "<p>You may change your password here. Upon successfully changing your password, <b>you will be required to login again</b>.</p>"

    current_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(min_length=8, widget=forms.PasswordInput(), help_text=PASSWORD_HELP_TEXT)
    confirm_password = forms.CharField(min_length=8, widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password", "")

        # Check requested password and confirmation match
        if new_password != cleaned_data.get("confirm_password", ""):
            self.add_error("confirm_password", "Password confirmation must match newly requested password")

        # Check current password
        if not check_password(cleaned_data.get("current_password"), self.db_password):
            self.add_error("current_password", "Invalid password")


class Change_Pronouns_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Pronouns"
    heading = "Change Pronouns"
    attrs = {"method": "POST"}
    text_prefix = "<p>Select your pronouns so that other can know how to refer to you.</p>"

    PRONOUN_CHOICES = (
        ("N/A", "Prefer not to say"),
        ("He/Him", "He/Him"),
        ("It/Its", "It/Its"),
        ("She/Her", "She/Her"),
        ("They/Them", "They/Them"),
        ("CUSTOM", "Custom (specify below)")
    )

    pronouns = Museum_Choice_Field(widget=forms.RadioSelect(), choices=PRONOUN_CHOICES)
    custom = forms.CharField(required=False)


class Change_Username_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Username"
    heading = "Change Username"
    attrs = {"method": "POST"}
    text_prefix = "<p>You may use this form to change your username. Afterwards, <b>you will be required to login again</b> with your new username and password.</p>"

    current_password = forms.CharField(widget=forms.PasswordInput())
    new_username = forms.CharField()
    confirm_username = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        new_username = cleaned_data.get("new_username", "")

        # Check requested username and confirmation match
        if new_username != cleaned_data.get("confirm_username", ""):
            self.add_error("confirm_username", "Username confirmation must match newly requested username")

        # Check prohibited characters
        if "/" in new_username:
            self.add_error("new_username", "Usernames may not contain slashes")

        # Check availability
        if User.objects.filter(username__iexact=new_username).exists():
            self.add_error("new_username", "Requested username is unavailable")

        # Check password
        if not check_password(cleaned_data.get("current_password"), self.db_password):
            self.add_error("current_password", "Invalid password")


class Forgot_Password_Form(forms.Form):
    use_required_attribute = False
    heading = "Forgot Password"
    submit_value = "Request Password Reset"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Please provide the email address for your account. If an account with that email address exists, "
        "a message will be sent to that address containing a link to reset your password.</p>"
    )

    email = forms.EmailField(label="Account email address")


class Forgot_Username_Form(forms.Form):
    use_required_attribute = False
    heading = "Forgot Username"
    submit_value = "Find Username"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Please provide the email address for your account. If an account with that email address exists, "
        "a message will be sent to that address providing your username.</p>"
    )

    email = forms.EmailField(label="Account email address")


class Login_Form(forms.Form):
    use_required_attribute = False
    heading = "Account Login"
    submit_value = "Login"
    attrs = {"method": "POST"}
    action = forms.CharField(widget=forms.HiddenInput(), initial="login")
    username = forms.CharField(help_text="<a href='/user/forgot-username/' tabindex='-1'>Forgot Username</a>")
    password = forms.CharField(help_text="<a href='/user/forgot-password/' tabindex='-1'>Forgot Password</a>", widget=forms.PasswordInput())


class Resend_Account_Activation_Email_Form(forms.Form):
    use_required_attribute = False
    heading = "Resend Account Activation Email"
    submit_value = "Resend Activation Email"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>If you haven't received your account activation email or your activation token has expired you can provide your email address here "
        "to have another one sent to your account.</p>"
        "<p>If you continue to not receive an activation email, contact "
        "<a href='mailto:{}'>Dr. Dos</a> for manual account activation..</p>".format(EMAIL_ADDRESS)
    )

    email = forms.EmailField()


class Reset_Password_Form(forms.Form):
    use_required_attribute = False
    heading = "Reset Password"
    submit_value = "Change Password"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Your request has been received. If the provided email has an associated account, an email will be sent to containing a token to reset "
        "your password. A link is also provided to automatically enter the token's value. This token will expire in 10 minutes.</p>"
        "<p>If no message is received, check your spam folder and wait a few minutes before trying again. If the issue persists, contact "
        "<a href='mailto:{}'>Dr. Dos</a>.</p>".format(EMAIL_ADDRESS)
    )

    reset_token = forms.CharField()
    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(),
        help_text=PASSWORD_HELP_TEXT
    )
    confirm_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput()
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password", "")

        # Check requested password and confirmation match
        if new_password != cleaned_data.get("confirm_password", ""):
            self.add_error("confirm_password", "Password confirmation must match newly requested password")

        # Check the token is valid
        qs = User.objects.filter(profile__reset_token=cleaned_data.get("reset_token"))

        if len(qs) != 1:
            self.add_error("reset_token", "The provided reset token is either invalid or expired.")
        else:
            delta = qs[0].profile.reset_time + timedelta(minutes=10)
            if datetime.now(timezone.utc) > delta:
                self.add_error("reset_token", "The provided reset token is either invalid or expired.")
            else:
                self.user = qs[0]
        return cleaned_data


class Updated_Terms_Of_Service_Form(forms.Form):
    use_required_attribute = False
    heading = "Updated Terms of Service"
    submit_value = "Accept Terms of Service"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>The Museum of ZZT's terms of service have been updated since you last agreed to the terms. In order to continue using your account you "
        "must accept the current version of the terms.</p>"
    )

    terms = Museum_TOS_Field()

    def clean(self):
        cleaned_data = super().clean()

        # Adjust TOS error message
        if not cleaned_data.get("terms"):
            self.add_error("terms", "You must agree to the terms of service in order to register an account.")
        return cleaned_data


class User_Registration_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Register Account"
    heading = "Register Account"
    attrs = {"method": "POST"}

    requested_username = forms.CharField(label="Username")
    requested_email = forms.EmailField(label="Email address", help_text="A valid email address is required to verify your account.")
    action = forms.CharField(widget=forms.HiddenInput(), initial="register")
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(), help_text=PASSWORD_HELP_TEXT)
    confirm_password = forms.CharField(min_length=8, widget=forms.PasswordInput(),)
    terms = Museum_TOS_Field()
    experiment = forms.CharField(label="Experiment", required=False)

    def clean(self):
        cleaned_data = super().clean()

        # Check if username is taken
        if User.objects.filter(username__iexact=cleaned_data.get("requested_username")).exists():
            self.add_error("requested_username", "Requested username is unavailable")

        # Check if email is taken
        if User.objects.filter(email=cleaned_data.get("requested_email")).exists():
            self.add_error("requested_email", "Requested email address is unavailable.")

        # Check passwords match
        if cleaned_data.get("password", "") != cleaned_data.get("confirm_password", ""):
            self.add_error("confirm_password", "Password confirmation must match password")

        # Adjust TOS error message
        if not cleaned_data.get("terms"):
            self.add_error("terms", "You must agree to the terms of service in order to register an account.")

        return cleaned_data
