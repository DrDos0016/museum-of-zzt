import random

from datetime import datetime

from django.db import models
from museum_site.models import File


class Poll(models.Model):
    title = models.CharField(max_length=80)
    start_date = models.DateField()
    end_date = models.DateField()
    secret = models.CharField(max_length=32, blank=True, default="")
    option1 = models.ForeignKey(
        "Option", related_name='option1', on_delete=models.SET_NULL, null=True
    )
    option2 = models.ForeignKey(
        "Option", related_name='option2', on_delete=models.SET_NULL, null=True
    )
    option3 = models.ForeignKey(
        "Option", related_name='option3', on_delete=models.SET_NULL, null=True
    )
    option4 = models.ForeignKey(
        "Option", related_name='option4', on_delete=models.SET_NULL, null=True
    )
    option5 = models.ForeignKey(
        "Option", related_name='option5', on_delete=models.SET_NULL, null=True
    )

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
        output = "Poll running {} through {}".format(
            self.start_date, self.end_date
        )
        return output


class Vote(models.Model):
    poll = models.ForeignKey("Poll", on_delete=models.SET_NULL, null=True)
    ip = models.GenericIPAddressField(default="")
    timestamp = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    option = models.ForeignKey("Option", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        formatted = "Poll #{poll} - Vote {option} by {email}".format(
            poll=self.poll_id, email=self.email, option=self.option_id
        )
        return formatted


class Option(models.Model):
    summary = models.CharField(max_length=300)
    backer = models.BooleanField(default=False)
    file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.file.title + " by " + self.file.author
