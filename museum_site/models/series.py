import os

from django.db import models
from django.db.models import Subquery
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from museum.settings import STATIC_URL
from museum_site.common import STATIC_PATH, epoch_to_unknown
from museum_site.models.base import BaseModel


class SeriesManager(models.Manager):
    def directory(self):
        qs = self.filter(visible=True)
        return qs


class Series(BaseModel):
    objects = SeriesManager()
    model_name = "Series"
    table_fields = ["Series", "Newest Entry", "Oldest Entry", "Articles"]
    sort_options = [
        {"text": "Newest Entry", "val": "latest"},
        {"text": "Title", "val": "title"}
    ]
    sort_keys = {
        # Key - Value from <select> used in GET params
        # Value - Django order_by param
        "title": "title",
        "latest": "-last_entry_date",
        "id": "id",
        "-id": "-id",
    }

    # Constants
    PREVIEW_DIRECTORY = os.path.join(STATIC_URL, "pages/series-directory/")
    PREVIEW_DIRECTORY_FULL_PATH = os.path.join(
        STATIC_PATH, "pages/series-directory/"
    )

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
        if self.id:
            article_set = self.article_set.all()
            if article_set:
                self.first_entry_date = (
                    article_set.order_by("publish_date").first().publish_date
                )
                self.last_entry_date = (
                    article_set.order_by("publish_date").last().publish_date
                )
        else:
            self.first_entry_date = "1970-01-01"
            self.last_entry_date = "1970-01-01"

        # Prevent blank preview URLs
        if not self.preview:
            self.preview = self.slug + ".png"
        super(Series, self).save(*args, **kwargs)

    def url(self):
        return "/series/{}/{}/".format(self.id, self.slug)

    def preview_url(self):
        return os.path.join(self.PREVIEW_DIRECTORY, self.preview)

    def detailed_block_context(self, *args, **kwargs):
        """ Return info to populate a detail block """
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title={"datum": "title", "value": self.title, "url": self.url},
            columns=[],
        )

        context["columns"].append([
            {"datum": "text", "label": "Newest Entry", "value": self.last_entry_date},
            {"datum": "text", "label": "Oldest Entry", "value": epoch_to_unknown(self.first_entry_date)},
            {"datum": "text", "label": "Articles", "value": self.article_set.count()},
            {"datum": "text", "value": mark_safe("<p>{}</p>".format(self.description))},
        ])

        return context

    def list_block_context(self, *args, **kwargs):
        context = dict(
            pk=self.pk,
            model=self.model_name,
            url=self.url,
            cells=[
                {"datum": "link", "url": self.url(), "value": self.title, "tag": "td"},
                {"datum": "text", "value": self.last_entry_date, "tag": "td"},
                {"datum": "text", "value": epoch_to_unknown(self.first_entry_date), "tag": "td"},
                {"datum": "text", "value": self.article_set.count(), "tag": "td"},
            ],
        )

        return context

    def gallery_block_context(self, *args, **kwargs):
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title={"datum": "title", "url": self.url(), "value": self.title},
            columns=[],
        )

        context["columns"].append([
            {"datum": "text", "value": self.last_entry_date}
        ])

        return context
