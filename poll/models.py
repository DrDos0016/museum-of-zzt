import random

from datetime import datetime

from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property

from museum_site.models import File


class Poll(models.Model):
    title = models.CharField(max_length=80)
    start_date = models.DateField()
    end_date = models.DateField()
    secret = models.CharField(max_length=32, blank=True, default="")
    options = models.ManyToManyField("Option", default=None, blank=True)

    def save(self, *args, **kwargs):
        # Pre save
        if self.secret == "":
            while len(self.secret) < 8:
                self.secret += random.choice("0123456789ABCDEF")

        # Actual save call
        super(Poll, self).save(*args, **kwargs)

    @property
    def active(self):
        today = datetime.now()
        today = today.date()
        return ((today >= self.start_date) and (today <= self.end_date))

    def __str__(self):
        output = "[{}] {}".format(self.pk, self.title)
        return output

    @cached_property
    def get_options(self, random_order=True):
        output = []
        qs = self.options.all()
        if random_order:
            qs = qs.order_by("?")
        return qs


    def get_all_choices(self):
        choices = []
        if option1 is not None:
            choices.append(option1)
        if option2 is not None:
            choices.append(option2)
        if option3 is not None:
            choices.append(option3)
        if option4 is not None:
            choices.append(option4)
        if option5 is not None:
            choices.append(option5)

        return choices

    def get_results(self):
        results = {}

        # Get all options
        options = self.get_options
        for option in options:
            results[option.pk] = {"option": option, "votes": 0, "winner": False}

        # Get all votes
        seen_emails = []
        votes = Vote.objects.filter(poll_id=self.pk).order_by("-id")
        for vote in votes:
            if vote.email in seen_emails:
                continue
            seen_emails.append(vote.email)
            results[vote.option_id]["votes"] += 1

        # Determine winner(s)
        winning_number = 0
        key_list = list(results.keys())
        # Determine max votes
        for k in key_list:
            if results[k]["votes"] > winning_number:
                winning_number = results[k]["votes"]
        for k in key_list:
            if results[k]["votes"] == winning_number:
                results[k]["winner"] = True
        return results


class Vote(models.Model):
    poll = models.ForeignKey("Poll", on_delete=models.SET_NULL, null=True)
    ip = models.GenericIPAddressField(default="")
    timestamp = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(default="", blank=True)
    option = models.ForeignKey("Option", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        formatted = "Poll #{poll} - Vote {option} by {email}".format(
            poll=self.poll_id, email=self.email, option=self.option_id
        )
        return formatted

    def scrub(self):
        self.ip = "127.0.0.1"
        self.email = ""


class Option(models.Model):
    title_override = models.CharField(max_length=120, default="", blank=True)
    author_override = models.CharField(max_length=120, default="", blank=True)
    preview_image_override = models.CharField(max_length=120, blank=True, help_text="Preview Image used instead of ZFile preview image")
    summary = models.CharField(max_length=300)
    backer = models.BooleanField(default=False)
    played = models.BooleanField(default=False)
    file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True)
    requested_by = models.CharField(max_length=80, default="", blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["played", "file__title"]

    def save(self, *args, **kwargs):
        if self.preview_image_override.startswith("/static/"):
            self.preview_image_override = self.preview_image_override[8:]
        super(Option, self).save(*args, **kwargs)

    def __str__(self):
        checked = "X" if self.played else " "
        requested = "(Patron)" if self.requested_by else ""
        title = self.title_override if self.title_override else self.file.title
        return '[{}] "{}" by {} {}'.format(checked, title, ", ".join(self.file.related_list("authors")), requested)

    def scrub(self):
        self.requested_by = ""

    def get_title(self):
        return self.title_override if self.title_override else self.file.title
