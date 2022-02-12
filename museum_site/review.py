from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from museum_site.datum import *
from museum_site.base import BaseModel
from museum_site.common import STATIC_PATH, epoch_to_unknown
from museum_site.templatetags.zzt_tags import char


class Review(BaseModel):
    """ Review object repesenting an review to a file """
    model_name = "Review"
    table_fields = ["Title", "File", "Reviewer", "Date", "Rating"]
    sort_options = [
        {"text": "Newest", "val": "-date"},
        {"text": "Oldest", "val": "date"},
        {"text": "File", "val": "file"},
        {"text": "Reviewer", "val": "reviewer"},
        {"text": "Rating", "val": "rating"},
    ]

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

    @mark_safe
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

    def url(self):
        return self.zfile.review_url() + "#rev-{}".format(self.id)

    def preview_url(self):
        return self.zfile.preview_url()

    def as_detailed_block(self, debug=False):
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
        )

        context["columns"].append([
            LinkDatum(
                label="File", value=self.zfile.title,
                url=self.zfile.url()
            ),
            TextDatum(label="Reviewer", value=self.author_link()),
            TextDatum(label="Date", value=epoch_to_unknown(self.date)),
        ])

        if self.rating >= 0:
            context["columns"][0].append(
                TextDatum(label="Rating", value="{} / 5.0".format(self.rating)),
            )

        if debug:
            context["columns"][0].append(
                LinkDatum(
                    label="ID", value=self.id, target="_blank", kind="debug",
                    url="/admin/museum_site/review/{}/change/".format(self.id),
                ),
            )

        return render_to_string(template, context)

    def as_list_block(self, debug=False):
        template = "museum_site/blocks/generic-list-block.html"
        #table_fields = ["Title", "File", "Reviewer", "Date", "Rating"]
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
                LinkDatum(
                    url=self.zfile.url(),
                    value=self.zfile.title,
                    tag="td",
                ),
                TextDatum(value=self.author_link(), tag="td"),
                TextDatum(value=epoch_to_unknown(self.date), tag="td"),
                TextDatum(value=("—" if self.rating < 0 else self.rating), tag="td"),
            ],
        )

        return render_to_string(template, context)

    def as_gallery_block(self, debug=False):
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
            TextDatum(value=self.author_link()),
        ])

        if self.rating >= 0:
            context["columns"][0].append(
                TextDatum(value="{} / 5.0".format(self.rating)),
            )

        if debug:
            context["columns"][0].append(
                LinkDatum(
                    value=self.id, target="_blank", kind="debug",
                    url="/admin/museum_site/review/{}/change/".format(self.id),
                ),
            )

        return render_to_string(template, context)
