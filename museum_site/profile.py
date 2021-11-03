from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify

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
    patronage = models.IntegerField(default=0)
    patron_email = models.EmailField(blank=True, unique=True)
    patron_tier = models.CharField(max_length=10, default=0)
    patron_visibility = models.BooleanField(default=True)
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
    files_published = models.IntegerField(default=0)
    pronouns = models.CharField(max_length=50, blank=True)

    # Account activation
    activation_token = models.CharField(max_length=64, blank=True)
    activation_time = models.DateTimeField(null=True, blank=True)
    accepted_tos = models.CharField(max_length=10, blank=True)

    # Password reset
    reset_token = models.CharField(max_length=64, blank=True)
    reset_time = models.DateTimeField(null=True, blank=True)

    # Patron perks
    stream_poll_nominations = models.TextField(max_length=2000, blank=True)
    stream_selections = models.TextField(max_length=2000, blank=True)
    closer_look_nominations = models.TextField(max_length=2000, blank=True)
    guest_stream_selections = models.TextField(max_length=2000, blank=True)
    closer_look_selections = models.TextField(max_length=2000, blank=True)
    bkzzt_topics = models.TextField(max_length=2000, blank=True)

    def __str__(self):
        return "Profile for user #{} - {}".format(
            self.user.id, self.user.username
        )

    def link(self):
        slug = slugify(self.user.username)
        return "/user/profile/{}/{}/".format(self.user.id, slug)

    def public_patron_status(self):
        if self.patron_visibility:
            return self.patron
        else:
            return False

    @property
    def get_pledge(self):
        strval = str(self.patronage)
        if self.patronage >= 100:
            amount = ("$" + strval[:-2] + "." + strval[-2:])
        elif self.patronage >= 10:
            amount = ("$0." + strval)
        else:
            amount = ("$0.0" + strval)
        return amount

    def scrub(self):
        self.patron = False
        self.patron_email = "test{}@example.com".format(self.user.id)
        self.patronage = 0
        self.patron_visibility = True
        self.patron_tier = "0"
        self.char = 2
        self.fg = "white"
        self.bg = "darkblue"
        self.site_credits_name = ""
        self.stream_credits_name = ""
        self.max_upload_size = UPLOAD_CAP
        self.files_published = 0
        self.pronouns = ""
        self.activation_token = ""
        self.activation_time = None
        self.accepted_tos = "2099-12-31"
        self.reset_token = ""
        self.reset_time = None
        self.stream_poll_nominations = ""
        self.stream_selections = ""
        self.closer_look_nominations = ""
        self.guest_stream_selections = ""
        self.closer_look_selections = ""
        self.bkzzt_topics = ""
        return True
