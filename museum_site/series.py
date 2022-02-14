import os

from django.db import models
from django.db.models import Subquery
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from museum.settings import STATIC_URL
from museum_site.common import STATIC_PATH, epoch_to_unknown
from museum_site.datum import *
from museum_site.base import BaseModel


class SeriesManager(models.Manager):
    def search(self, p):
        qs = self.exclude(visible=False)
        return qs


class Series(BaseModel):
    objects = SeriesManager()
    model_name = "Series"
    table_fields = ["Series", "Newest Entry", "Oldest Entry", "Articles"]
    sort_options = [
        {"text": "Newest Entry", "val": "latest"},
        {"text": "Title", "val": "title"}
    ]

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
        article_set = self.article_set.all()
        if self.id and article_set:
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
        return "/series/" + str(self.id) + "/" + self.slug

    def preview_url(self):
        return os.path.join(self.PREVIEW_DIRECTORY, self.preview)

    def as_detailed_block(self, debug=False, extras=[]):
        template = "museum_site/blocks/generic-detailed-block.html"
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title=LinkDatum(
                value=self.title,
                url=self.url()
            ),
            columns=[],
            description=self.description
        )

        context["columns"].append([
            TextDatum(label="Newest Entry", value=self.last_entry_date),
            TextDatum(label="Oldest Entry", value=epoch_to_unknown(self.first_entry_date)),
            TextDatum(label="Articles", value=self.article_set.count()),
        ])

        if debug:
            context["columns"][0].append(
                LinkDatum(
                    label="ID", value=self.id, target="_blank", kind="debug",
                    url="/admin/museum_site/series/{}/change/".format(self.id),
                ),
            )

        return render_to_string(template, context)

    def as_list_block(self, debug=False, extras=[]):
        template = "museum_site/blocks/generic-list-block.html"
        context = dict(
            pk=self.pk,
            model=self.model_name,
            url=self.url,
            cells=[
                LinkDatum(
                    url=self.url(),
                    value=self.title,
                    tag="td",
                ),
                TextDatum(value=self.last_entry_date, tag="td"),
                TextDatum(value=epoch_to_unknown(self.first_entry_date), tag="td"),
                TextDatum(value=self.article_set.count(), kind="r", tag="td"),
            ],
        )

        return render_to_string(template, context)

    def as_gallery_block(self, debug=False, extras=[]):
        template = "museum_site/blocks/generic-gallery-block.html"
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title=self.title,
            columns=[],
        )

        context["columns"].append([
            TextDatum(value=self.last_entry_date),
        ])

        if debug:
            context["columns"][0].append(
                LinkDatum(
                    value=self.id, target="_blank", kind="debug",
                    url="/admin/museum_site/series/{}/change/".format(self.id),
                ),
            )

        return render_to_string(template, context)
