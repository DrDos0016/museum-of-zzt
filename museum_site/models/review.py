from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import timesince
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe

from museum_site.core.feedback_tag_identifiers import *
from museum_site.core.misc import profanity_filter
from museum_site.core.sorters import Feedback_Sorter
from museum_site.constants import DATE_HR
from museum_site.models.base import BaseModel
from museum_site.querysets.review_querysets import *


class Review(BaseModel):
    """ Feedback object repesenting feedback provided to a zfile """
    objects = Review_Queryset.as_manager()

    model_name = "Review"
    to_init = ["yours"]
    table_fields = ["Title", "File", "Author", "Date", "Rating"]
    table_widths = ["30%", "30%", "15%", "12%", "13%"]
    cell_list = ["view", "zfile", "author", "review_date", "rating"]
    guide_word_values = {"id": "pk", "reviewer": "reviewer", "date": "date", "file": "zfile", "rating": "rating"}
    sorter = Feedback_Sorter

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
    tags = models.ManyToManyField(
        "Feedback_Tag", default=None, blank=True,
        help_text="Tag your feedback to identify what kind of information it provides. Any feedback with a rating will be automatically tagged as a review."
    )
    spotlight = models.BooleanField(default=True, help_text="Boolean to mark feedback as suitable for display on the front page.")

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        if self.zfile:
            output = "[{}] Review of '{}' [{}] by {}".format(
                self.id,
                self.zfile.title,
                self.zfile.filename,
                self.author
            )
        else:
            output = "Review Object"
        return output

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


    @cached_property
    def get_tags(self):
        return self.tags.all()

    def filtered_content(self):
        return self.content
        return profanity_filter(self.content)

    def scrub(self):
        self.user_id = None
        self.ip = ""

    def url(self):
        if self.zfile is None:
            return "#rev-XX"
        return self.zfile.review_url() + "#rev-{}".format(self.id)

    def get_absolute_url(self):
        if self.zfile is None:
            return "#rev-XX"
        return self.zfile.review_url() + "#rev-{}".format(self.pk)

    def preview_url(self):
        return self.zfile.preview_url()

    def save(self, *args, **kwargs):
        if self.author == "":
            self.author = "Anonymous"
        if self.user_id:
            self.author = self.user.username

        super(Review, self).save(*args, **kwargs)

    def get_field_view(self, view="detailed"):
        return {"value": "<a href='{}'>{}</a>".format(self.get_absolute_url(), self.title or "<i>Untitled Review</i>"), "safe": True}

    def get_field_zfile(self, view="detailed"):
        return {"label": "File", "value": self.zfile.get_field_view("title")["value"], "safe": True}

    def get_field_author(self, view="detailed"):
        return {"label": "Submitted By", "value": self.author_link(), "safe": True}

    def get_field_review_date(self, view="detailed"):
        if view == "review_content":
            if self.date:
                return {"label": "Date", "value": "{} ago ({})".format(timesince(self.date), self.date.strftime(DATE_HR)), "safe": True}
            else:
                return {"label": "Date", "value": ""}
        else:
            return {"label": "Date", "value": self.date.strftime(DATE_HR), "safe": True}

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
        value = self.content
        if self.pk and self.pk > 2000 and self.zfile_id and self.zfile.publish_date and str(self.zfile.publish_date) != "2018-11-06 00:00:00+00:00":
            if self.zfile.publish_date > self.date:
                value = "**__This feedback was submitted prior to publication of this file and may not reflect its current contents__**\n\n" + value

        return {"label": "Feedback", "value": value, "markdown": True}

    def get_field_reviewer_link(self, view="review-content"):
        url = reverse("review_browse_author", kwargs={"author": self.author.lower()})
        return {"value": "<a href='{}'>Other feedback given by {}</a>".format(url, self.author), "safe": True}

    def get_field_tags(self, view="review-content"):
        tags = None
        if self.zfile:
            tags = list(self.tags.all().order_by("title").values_list("title", flat=True))
        if not tags:
            tags = ["<i>None</i>"]
        return {"label": "Tags", "value": ", ".join(tags), "safe": True}

    def get_field_edit_feedback(self, view="review-content"):
        pk = self.pk if self.pk else 1
        return self.field_context(url=reverse("feedback_edit", kwargs={"pk": pk}), text="Edit Feedback")

    def get_field_delete_feedback(self, view="review-content"):
        return self.field_context(url=reverse("feedback_delete_confirm") + "?pk={}".format(self.pk), text="Delete Feedback")


    def context_universal(self, request=None):
        context = super().context_universal(request)
        context["model_key"] = "rev-{}".format(context["model_key"])
        return context

    def context_detailed(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "detailed"]
        context["columns"] = []

        columns = [
            ["zfile", "author", "review_date", "tags"],
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

        for field_name in self.cell_list:
            cell_fields = self.get_field(field_name, view="list")
            context["cells"].append(cell_fields)
        return context

    def context_gallery(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "gallery"]
        context["fields"] = [
            self.get_field("rating", view="gallery"),
            self.get_field("author", view="gallery"),
        ]
        return context

    def context_review_content(self):
        # Context used when displaying a full review
        context = self.context_universal()
        context["roles"] = ["model-block", "review-content"]
        context["show_actions"] = True
        context["fields"] = []
        field_list = ["author", "review_date", "tags", "content", "rating"]

        if not self.pk:
            field_list.remove("tags")
        elif not self.is_tagged(FEEDBACK_TAG_REVIEW):
            field_list.remove("rating")

        for field_name in field_list:
            field_context = self.get_field(field_name, view="review_content")
            if field_context:
                context["fields"].append(field_context)

        action_list = ["reviewer_link"]
        if self.is_yours:
            action_list.append("edit_feedback")
            action_list.append("delete_feedback")

        actions = []
        for action in action_list:
            actions.append(self.get_field(action, view="detailed"))
        context["actions"] = actions

        return context

    def get_guideword_date(self): return self.date.strftime(DATE_HR)
    def get_guideword_reviewer(self): return self.author
    def get_guideword_rating(self):
        if self.rating < 0:
            return "<i>-No Rating-</i>"
        else:
            return self.rating
    def get_guideword_zfile(self): return self.zfile.title

    def is_tagged(self, tag_id):
        if self.pk and tag_id in self.tags.all().values_list("id", flat=True):
            return True
        return False

    def _init_yours(self):
        """ Determine if the item is "yours" """
        self.is_yours = False
        if self.request and self.user:
            self.is_yours = True if self.request.user.pk == self.user.pk else False

    def process_kwargs(self, kwargs):
        if kwargs.get("hide_actions"):
            self.context["show_actions"] = False

class Feedback_Tag(models.Model):
    TAGS = (
        ("Bug Report", "Bug Report"),
        ("Changelog", "Changelog"),
        ("Content Warning", "Content Warning"),
        ("Hints and Solutions", "Hints and Solutions"),
        ("Review", "Review"),
        ("Table of Contents", "Table of Contents"),
    )

    title = models.CharField(choices=TAGS, max_length=25)
    key = models.CharField(max_length=20)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

