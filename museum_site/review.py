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
    PROFANITY = ["graphics", "coherency", "wtf"]

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

    def get_content(self, profanity=False):
        if profanity:
            return self.content
        else:
            output = []
            words = self.content.split(" ")
            for word in words:
                for p in self.PROFANITY:
                    if word.lower().find(p) != -1:
                        print("P is", p, len(p))
                        word = word.lower().replace(p, ("*" * len(p)))
                        print(word)
                output.append(word)

        return " ".join(output)


    def scrub(self):
        self.user_id = None
        self.ip = ""

    def url(self):
        return self.zfile.review_url() + "#rev-{}".format(self.id)

    def preview_url(self):
        return self.zfile.preview_url()

    def as_detailed_block(self, debug=False, extras=[]):
        template = "museum_site/blocks/generic-detailed-block.html"
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title=LinkDatum(
                value=mark_safe(self.title if self.title else "<i>Untitled Review</i>"),
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

    def as_list_block(self, debug=False, extras=[]):
        template = "museum_site/blocks/generic-list-block.html"
        context = dict(
            pk=self.pk,
            model=self.model_name,
            url=self.url,
            cells=[
                LinkDatum(
                    url=self.url(),
                    value=self.title if self.title else "Untitled",
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

    def as_gallery_block(self, debug=False, extras=[]):
        template = "museum_site/blocks/generic-gallery-block.html"
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title=LinkDatum(
                    url=self.url(),
                    value=self.title if self.title else "Untitled",
                ),
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

    def detailed_block_context(self, extras=None, *args, **kwargs):
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title={"datum": "title", "value":mark_safe(self.title if self.title else "<i>Untitled Review</i>"), "url":self.url()},
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
                {"datum": "link", "url":self.url(), "value":self.title if self.title else "Untitled", "tag":"td"},
                {"datum": "link", "url":self.zfile.url(), "value":self.zfile.title, "tag":"td"},
                {"datum": "text", "value":self.author_link(), "tag":"td"},
                {"datum": "text", "value":epoch_to_unknown(self.date), "tag":"td"},
                {"datum": "text", "value":("—" if self.rating < 0 else self.rating), "tag":"td"}
            ],
        )
        return context

    def gallery_block_context(self, extras=None, *args, **kwargs):
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title={"datum": "link", "url":self.url(), "value":self.title if self.title else "Untitled"},
            columns=[],
        )

        context["columns"].append([
            {"datum": "text", "value":self.author_link()},
        ])

        if self.rating >= 0:
            context["columns"][0].append(
                {"datum": "text", "value":"{} / 5.0".format(self.rating)}
            )
        return context
