from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from museum_site.common import UPLOAD_CAP


class Profile(models.Model):
    """ Profile object repesenting a user's profile
    Do not query directly. This is pulled automatically in
    context_processors.py for any logged in user.

    Fields:
    user            -- ID of User object
    patron
    """

    FG_CHOICES = [
        ("gray", "Dark Gray"),
        ("blue", "Blue"),
        ("green", "Green"),
        ("cyan", "Cyan"),
        ("red", "Red"),
        ("purple", "Purple"),
        ("yellow", "Yellow"),
        ("white", "White"),
        ("black", "Black"),
        ("blue", "Dark Blue"),
        ("green", "Dark Green"),
        ("cyan", "Dark Cyan"),
        ("red", "Dark Red"),
        ("purple", "Dark Purple"),
        ("yellow", "Dark Yellow"),
        ("gray", "Gray"),
    ]

    BG_CHOICES = list(FG_CHOICES).append(("transparent", "Transparent"))

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    patron = models.BooleanField(default=False)
    patron_level = models.IntegerField(default=0)
    char = models.IntegerField(default=2)
    fg = models.CharField(max_length=11, default="white")
    bg = models.CharField(max_length=11, default="darkblue")
    site_credits_name = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )
    stream_credits_name = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )
    max_upload_size = models.IntegerField(default=UPLOAD_CAP)
    files_uploaded = models.IntegerField(default=0)
    pronouns = models.CharField(max_length=50)

    # Password reset
    reset_token = models.CharField(max_length=64, blank=True)
    reset_time = models.DateTimeField(null=True, blank=True)