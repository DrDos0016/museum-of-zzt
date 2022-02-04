from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from museum_site.templatetags.zzt_tags import char


class Review(models.Model):
    """ Review object repesenting an review to a file """
    model_name = "Review"

    """
    Fields:
    zfile            -- Link to File object
    title           -- Title of the review
    author          -- Author of the review
    content         -- Body of review
    rating          -- Rating given to file from 0.0 - 5.0
    date            -- Date review was written
    ip              -- IP address posting the review
    """
    zfile = models.ForeignKey("File", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50, blank=True, null=True)
    content = models.TextField()
    rating = models.FloatField(default=5.0)
    date = models.DateField()
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        output = "[{}] Review of '{}' [{}] by {}".format(
            self.id,
            self.zfile.title,
            self.zfile.filename,
            self.author
        )
        return output

    def author_link(self):
        if self.user:
            link = '{} <a href="{}">{}</a>'.format(
                char(
                    self.user.profile.char, self.user.profile.fg,
                    self.user.profile.bg, scale=2
                ),
                self.user.profile.link(),
                self.user.username
            )
        else:
            link = self.author

        return link

    def get_author(self):
        # Returns a string of the username on a review if one exists,
        # or the manually set name
        if self.user:
            output = self.user.username
        else:
            output = self.author

        if output == "":
            output = "Unknown"
        return output

    def scrub(self):
        self.user_id = None
        self.ip = ""
