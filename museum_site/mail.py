import smtplib
import ssl

from django.conf import settings
from django.contrib.auth.models import User
from museum_site.core.misc import record
from museum_site.constants import *
from museum_site.models import *
from museum_site.settings import SMTP_HOST, SMTP_PORT, SMTP_AUTH_USER, SMTP_AUTH_PASS

NOREPLY = "noreply@museumofzzt.com"


def send(to, frm, subj, body):
    if settings.ENVIRONMENT != "DEV":
        message = """From: Museum of ZZT <{}>
To: <{}>
Subject: {}

{}""".format(frm, to[0], subj, body)
        s = smtplib.SMTP(SMTP_HOST, port=SMTP_PORT)
        if SMTP_AUTH_USER != "-UNDEFINED-" and SMTP_AUTH_PASS != "-UNDEFINED-":
            s.login(SMTP_AUTH_USER, SMTP_AUTH_PASS)
        s.sendmail(frm, to, message)
    else:
        record("========== DEBUG EMAIL ==========")
        record(to, frm, subj, body)
        record("=================================")


def send_account_verification_email(user, domain):
    to = [user.email]
    frm = NOREPLY
    subj = "Verify Your Museum of ZZT Account"
    body_template = """
Hello!

A request was recently submitted to create an account with the Museum of ZZT.

You can verify your account by visiting the following link:
https://{}

Alternatively, you may manually supply the verification token of: {}
"""

    body = body_template.format(domain, user.profile.activation_token)
    send(to, frm, subj, body)
    return True


def send_forgotten_password_email(user, domain):
    to = [user.email]
    frm = NOREPLY
    subj = "Museum of ZZT Password reset verification"
    body_template = """
Hello!

A request was recently submitted to reset the password associated with this
account on the Museum of ZZT.

You can choose a new password by visiting the following link:
https://{}

Alternatively, you may manually supply the your reset token of: {}

This reset token will only be accepted for 10 minutes.
"""

    body = body_template.format(domain, user.profile.reset_token)
    send(to, frm, subj, body)
    return True


def send_forgotten_username_email(user):
    to = [user.email]
    frm = NOREPLY
    subj = "Museum of ZZT Forgotten username reminder"
    body_template = """
Hello!

A request was recently submitted to retreive a forgotten username on the
Museum of ZZT.

Your username is: {}
"""

    body = body_template.format(user.username)
    send(to, frm, subj, body)
    return True
