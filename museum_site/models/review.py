from datetime import datetime


from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from museum_site.models.base import BaseModel
from museum_site.common import profanity_filter
from museum_site.core.misc import epoch_to_unknown
from museum_site.templatetags.zzt_tags import char
from museum_site.querysets.review_querysets import *


class Review(BaseModel):
    """ Review object repesenting an review to a file """
    objects = Review_Queryset.as_manager()

    model_name = "Review"
    table_fields = ["Title", "File", "Reviewer", "Date", "Rating"]
    sort_options = [
        {"text": "Newest", "val": "-date"},
        {"text": "Oldest", "val": "date"},
        {"text": "File", "val": "file"},
        {"text": "Reviewer", "val": "reviewer"},
        {"text": "Rating", "val": "rating"},
    ]
    sort_keys = {
        "-date": "-date",
        "date": "date",
        "file": "zfile__sort_title",
        "reviewer": "author",
        "rating": "-rating",
        "id": "id",
        "-id": "-id",
    }

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
    author = models.CharField(max_length=50)
    content = models.TextField()
    rating = models.FloatField(default=5.0)
    date = models.DateField()
    ip = models.GenericIPAddressField(blank=True, null=True)
    approved = models.BooleanField(default=True)

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
        elif self.author:
            link = self.author
        else:
            link = "Anonymous"

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

    def filtered_content(self):
        return self.content
        return profanity_filter(self.content)

    def scrub(self):
        self.user_id = None
        self.ip = ""

    def url(self):
        return self.zfile.review_url() + "#rev-{}".format(self.id)

    def preview_url(self):
        return self.zfile.preview_url()

    def detailed_block_context(self, extras=None, *args, **kwargs):
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title={"datum": "title", "value": mark_safe(self.title if self.title else "<i>Untitled Review</i>"), "url": self.url()},
            columns=[],
        )

        context["columns"].append([
            {"datum": "link", "label": "File", "value": self.zfile.title, "url": self.zfile.url()},
            {"datum": "text", "label": "Reviewer", "value": self.author_link()},
            {"datum": "text", "label": "Date", "value": epoch_to_unknown(self.date)},
        ])

        if self.rating >= 0:
            context["columns"][0].append(
                {"datum": "text", "label": "Rating", "value": "{} / 5.0".format(self.rating)},
            )

        return context

    def list_block_context(self, extras=None, *args, **kwargs):
        context = dict(
            pk=self.pk,
            model=self.model_name,
            url=self.url,
            cells=[
                {"datum": "link", "url": self.url(), "value": self.title if self.title else "Untitled", "tag": "td"},
                {"datum": "link", "url": self.zfile.url(), "value": self.zfile.title, "tag": "td"},
                {"datum": "text", "value": self.author_link(), "tag": "td"},
                {"datum": "text", "value": epoch_to_unknown(self.date), "tag": "td"},
                {"datum": "text", "value": ("—" if self.rating < 0 else self.rating), "tag": "td"}
            ],
        )
        return context

    def gallery_block_context(self, extras=None, *args, **kwargs):
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title={"datum": "link", "url": self.url(), "value": self.title if self.title else "Untitled"},
            columns=[],
        )

        context["columns"].append([
            {"datum": "text", "value": self.author_link()},
        ])

        if self.rating >= 0:
            context["columns"][0].append(
                {"datum": "text", "value": "{} / 5.0".format(self.rating)}
            )
        return context

    def review_content_block_context(self, extras=None, *args, **kwargs):
        context = dict(
            pk=self.pk,
            model=self.model_name,
            title=self.title,
            author=self.author,
            author_link=self.author_link(),
            date=self.date,
            today=datetime.now(),
            review_content=self.content,
            rating=self.rating,
            debug = kwargs["request"].session.get("DEBUG") if kwargs.get("request") else False
        )

        return context

    def save(self, *args, **kwargs):
        if self.author == "":
            self.author = "Anonymous"
        super(Review, self).save(*args, **kwargs)
