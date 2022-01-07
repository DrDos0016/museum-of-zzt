from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from museum_site.templatetags.zzt_tags import char


class Review(models.Model):
    """ Review object repesenting an review to a file

    Fields:
    file            -- Link to File object
    title           -- Title of the review
    author          -- Author of the review
    content         -- Body of review
    rating          -- Rating given to file from 0.0 - 5.0
    date            -- Date review was written
    ip              -- IP address posting the review
    """
    file = models.ForeignKey("File", on_delete=models.SET_NULL, null=True)
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
        ordering = ["id"]

    def __str__(self):
        output = "[{}] Review of '{}' [{}] by {}".format(
            self.id,
            self.file.title,
            self.file.filename,
            self.author
        )
        return output

    def from_request(self, request):
        if request.method != "POST":
            return False

        if request.user.is_authenticated:
            self.author = request.user.username
            self.user = request.user
        else:
            self.author = request.POST.get("name")  # NAME not author

        self.file_id = int(request.POST.get("file_id"))
        self.title = request.POST.get("title")
        self.content = request.POST.get("content")
        self.rating = round(float(request.POST.get("rating")), 2)
        self.date = datetime.utcnow()
        self.ip = request.META["REMOTE_ADDR"]

        return True

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

    def scrub(self):
        self.user_id = None
        self.ip = ""
