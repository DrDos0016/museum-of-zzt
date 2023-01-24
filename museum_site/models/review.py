from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import timesince
from django.utils.safestring import mark_safe

from museum_site.common import profanity_filter
from museum_site.core.misc import epoch_to_unknown
from museum_site.models.base import BaseModel
from museum_site.querysets.review_querysets import *
from museum_site.templatetags.zzt_tags import char


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
        "-date": ["-date", "zfile__sort_title"],
        "date": ["date", "zfile__sort_title"],
        "file": ["zfile__sort_title"],
        "reviewer": ["author", "zfile__sort_title"],
        "rating": ["-rating", "zfile__sort_title"],
        "id": ["id"],
        "-id": ["-id"],
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
    date = models.DateTimeField(auto_now_add=True)
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

    def gallery_block_context(self, extras=None, *args, **kwargs):
        context = dict(
            pk=self.pk,
            hash_id = "review-{}".format(self.pk),
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
            hash_id = "review-{}".format(self.pk),
            model=self.model_name,
            title=self.title,
            author=self.author,
            author_link=self.author_link(),
            date=self.date,
            review_content=self.content,
            rating=self.rating,
            debug = True if kwargs.get("request") and kwargs["request"].session.get("DEBUG") else False
        )
        return context

    def save(self, *args, **kwargs):
        if self.author == "":
            self.author = "Anonymous"
        super(Review, self).save(*args, **kwargs)

    def get_field_view(self, view="detailed"):
        return {"value": "<a href='{}'>{}</a>".format(self.url(), self.title), "safe": True}

    def get_field_zfile(self, view="detailed"):
        self.zfile.init_actions()
        self.zfile._init_icons()
        return {"label": "File", "value": self.zfile.get_field_view("title")["value"], "safe": True}

    def get_field_author(self, view="detailed"):
        return {"label": "Reviewer", "value": self.author_link(), "safe": True}

    def get_field_review_date(self, view="detailed"):
        if view == "review_content":
            return {"label": "Review Date", "value": "{} ago ({})".format(timesince(self.date), self.date.strftime("%b %d, %Y")), "safe": True}
        else:
            return {"label": "Review Date", "value": self.date.strftime("%b %d, %Y"), "safe": True}

    def get_field_rating(self, view="detailed"):
        if self.rating is not None:
            long_rating = (str(self.rating) + "0")[:4]
            rating = "{} / 5.00".format(long_rating)
        else:
            rating = "<i>No rating</i>"

        if self.rating == -1:
            if view == "list":
                rating = "&mdash;"

            if view == "gallery":
                rating = ""

            if view == "review_content":
                rating = "<i>This user has opted out of providing a numeric rating</i>"
        if view == "review_content":
            rating = "<b>{}</b>".format(rating)

        output = {"label": "Rating", "value": rating, "safe": True}
        return output

    def get_field_content(self, view="review-content"):
        return {"label": "Review", "value": self.content, "markdown": True}

    def get_field_reviewer_link(self, view="review-content"):
        return {"value": "<a href='/review/author/{}/'>Other reviews written by {}</a>".format(self.author.lower(), self.author), "safe": True}


    def context_detailed(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "detailed"]
        context["columns"] = []

        columns = [
            ["zfile", "author", "review_date"],
        ]
        if self.rating != -1:  # Show numeric rating if the review has one
            columns[0].append("rating")

        for col in columns:
            column_fields = []
            for field_name in col:
                field_context = self.get_field(field_name)
                column_fields.append(field_context)
            context["columns"].append(column_fields)
        return context

    def context_list(self):
        context = self.context_universal()
        context["roles"] = ["list"]
        context["cells"] = []

        cell_list = ["view", "zfile", "author", "review_date", "rating"]
        for field_name in cell_list:
            cell_fields = self.get_field(field_name, view="list")
            context["cells"].append(cell_fields)
        return context

    def context_gallery(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "gallery"]
        context["fields"] = [
            self.get_field("author", view="gallery"),
            self.get_field("rating", view="gallery")
        ]
        return context

    def context_review_content(self):
        # Context used when displaying a full review
        context = self.context_universal()
        context["roles"] = ["model-block", "review-content"]
        context["show_actions"] = False
        context["fields"] = []
        field_list = ["author", "review_date", "content", "rating", "reviewer_link"]

        for field_name in field_list:
            field_context = self.get_field(field_name, view="review_content")
            context["fields"].append(field_context)
        return context
