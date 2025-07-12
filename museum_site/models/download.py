import os

from django.db import models
from django.urls import reverse

from museum_site.models.base import BaseModel
from museum_site.constants import SITE_ROOT


class Download(BaseModel):
    """ Download object representing a location to acquire a file"""
    model_name = "Download"

    KIND_CHOICES = [
        ("zgames", "Museum of ZZT Hosted"),
        ("itch", "Itch.io"),
        ("personal", "Personal Webpage"),
        ("other", "Other"),
    ]

    PRIORITIES = {
        "itch": 40,
        "personal": 30,
        "other": 20,
        "zgames": 0,
    }

    url = models.CharField(max_length=200)  # URL for download
    priority = models.IntegerField(default=10, editable=False)  # Priority for listing download sources (greater = more important)
    kind = models.CharField(max_length=100, choices=KIND_CHOICES, default="zgames")  # Location of download
    hosted_text = models.CharField(max_length=100, blank=True)  # String used for users to tell where a download is hosted

    class Meta:
        ordering = ["-priority"]

    def save(self, *args, **kwargs):
        self.priority = self.PRIORITIES.get(self.kind, 10)
        super(Download, self).save(*args, **kwargs)

    def __str__(self):
        return "[{}] {} - {}".format(self.id, self.kind, self.get_absolute_url())

    def get_absolute_url(self):
        return self.url

    def hosted_on(self):
        if self.kind == "zgames":
            return "Hosted on the Museum of ZZT"
        elif self.kind == "itch":
            return "Hosted on itch.io"
        elif self.hosted_text:
            return "Hosted on " + self.hosted_text
        elif self.kind == "personal":
            return "Hosted on the author's website"
        else:
            return "Hosted elsewhere"

    def logo(self):
        if self.kind == "zgames":
            src = "moz-dl-icon.png"
            alt = "Museum of ZZT"
        elif self.kind == "itch":
            src = "itchio-textless-white.svg"
            alt = "itch"
        else:
            src = "generic-download-logo.png"
            alt = "Generic"
        output = '<img src="/static/icons/{}" alt="{} Download Icon">'.format(src, alt)
        return output

    def zgame_exists(self):
        """ Return TRUE if the zipfile is physically available """
        return True if os.path.isfile(self.phys_path()) else False

    def phys_path(self):
        return os.path.join(SITE_ROOT, self.get_absolute_url()[1:])
