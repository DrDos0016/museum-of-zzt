from datetime import datetime

from django.db import models

from museum_site.models.base import BaseModel
from museum_site.common import slash_separated_sort, UPLOAD_CAP, STATIC_PATH
from museum_site.constants import SITE_ROOT, ZETA_RESTRICTED


class Download(BaseModel):
    """ Download object representing a place to acquire a file"""
    model_name = "Download"

    """
    Fields:
    url             -- URL for download
    priority        -- Priority for listing download sources
    kind            -- What is this download source
    """

    KIND_CHOICES = [
        ("itch", "Itch.io"),
        ("personal", "Personal Webpage"),
        ("other", "Other"),
    ]

    PRIORITIES = {
        "itch": 40,
        "personal": 30,
        "other": 20,
    }

    url = models.CharField(max_length=200)
    priority = models.IntegerField(default=10, editable=False)
    kind = models.CharField(
        max_length=100, choices=KIND_CHOICES, default="zgames"
    )
    hosted_text = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-priority"]

    def save(self, *args, **kwargs):
        self.priority = self.PRIORITIES.get(self.kind, 10)
        super(Download, self).save(*args, **kwargs)

    def __str__(self):
        return "[{}] {} - {}".format(self.id, self.kind, self.url)

    def hosted_on(self):
        if self.kind == "itch":
            return "Hosted on itch.io"
        elif self.hosted_text:
            return "Hosted on " + self.hosted_text
        elif self.kind == "personal":
            return "Hosted on the author's website"
        else:
            return "Hosted elsewhere"

    def logo(self):
        if self.kind == "itch":
            src = "itchio-textless-white.svg"
            alt = "itch"
        else:
            src = "generic-download-logo.png"
            alt = "Generic"
        output = '<img src="/static/icons/{}" alt="{} Download Icon">'.format(
            src, alt
        )
        return output