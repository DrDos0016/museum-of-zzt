from django.contrib.auth.models import User
from .common import *
from .constants import *
from .models import *

NOREPLY = "noreply@museumofzzt.com"


def send_account_verification_email(user, domain):
    to = [user.email]
    frm = NOREPLY
    subj = "Verify Your Museum of ZZT Account"
    body_template = """
Hello!

A request was recently submitted to create an account with the Museum of ZZT.

You can verify your account by visiting the following link:
{}

Alternativey, you may manually supply the verification token of: {}
"""

    body = body_template.format(domain, user.profile.activation_token)
    print(to, frm, subj, body)
    return True


def send_forgotten_password_email(user, domain):
    to = [user.email]
    frm = NOREPLY
    subj = "Password reset verification"
    body_template = """
Hello!

A request was recently submitted to reset the password associated with this
account on the Musuem of ZZT.

You can choose a new password by visiting the following link:
{}

Alternatively, you may manually supply the your reset token of: {}

This reset token will only be accepted for 10 minutes.
"""

    body = body_template.format(domain, user.profile.reset_token)
    print(to, frm, subj, body)
    return True


def send_forgotten_username_email(user):
    to = [user.email]
    frm = NOREPLY
    subj = "Forgotten username reminder"
    body_template = """
Hello!

A request was recently submitted to retreive a forgotten username on the
Musuem of ZZT.

Your username is: {}
"""

    body = body_template.format(user.username)
    print(to, frm, subj, body)
    return True
