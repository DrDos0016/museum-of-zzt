import os

from django.db import models
from django.db.models import Subquery
from django.template.defaultfilters import slugify

from museum.settings import STATIC_URL


class SeriesManager(models.Manager):
    def search(self, p):
        qs = self.exclude(visible=False)
        return qs

class Series(models.Model):
    objects = SeriesManager()

    # Constants
    PREVIEW_DIRECTORY = os.path.join(STATIC_URL, "pages/series-directory/")

    # Fields
    title = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, editable=False)
    description = models.TextField(default="")
    preview = models.CharField(max_length=80, default="", blank=True)
    first_entry_date = models.DateField()
    last_entry_date = models.DateField()
    visible = models.BooleanField(default=True)


    class Meta:
        ordering = ["title"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.first_entry_date = self.article_set.all().order_by("publish_date").first().publish_date
        self.last_entry_date = self.article_set.all().order_by("publish_date").last().publish_date
        super(Series, self).save(*args, **kwargs)

    def url(self):
        return "/series/" + str(self.id) + "/" + self.slug

    def preview_url(self):
        if self.preview:
            return os.path.join(self.PREVIEW_DIRECTORY, self.preview)
        else:
            return os.path.join(self.PREVIEW_DIRECTORY, self.slug + ".png")
