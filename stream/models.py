from datetime import datetime

from django.db import models

from museum_site.models.base import BaseModel


class Stream(BaseModel):
    model_name = "Stream"

    CATEGORY_CHOICES = (
        ("none", ""),
        ("wildcard", "Unpreserved Worlds"),
        ("theme", "Theme Stream"),
        ("bonus", "Bonus Stream"),
        ("new", "New Release Showcase"),
        ("guest", "Special Guest Stream"),
        ("community", "Community Event"),
        ("beyond", "Beyond Worlds of ZZT"),
        ("dev", "Game Dev Stream"),
    )

    title = models.CharField(max_length=120)
    key = models.CharField(max_length=30, help_text="Key to identify stream with", blank=True, default="")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=50, default="none")
    description = models.CharField(max_length=300)
    when = models.DateTimeField(help_text="6pm PST = 2:00 UTC next day. 12pm PST = 20:00 UTC")
    preview_image = models.CharField(max_length=120, help_text="Preview Image used on stream schedule", default="/static/screenshots/no_screenshot.png")
    entries = models.ManyToManyField("Stream_Entry", default=None, blank=True, help_text="Stream Entries to be played during this stream")
    visible = models.BooleanField(default=True)
    guests = models.CharField(max_length=300, help_text="Guests on stream", default=None, blank=True)
    theme = models.CharField(max_length=120, help_text="Theme for stream", default=None, blank=True)

    def when_in_pacific(self):
        print(self.when)
        print(self.when.tzinfo)
        return self.when

    def __str__(self):
        if self.when:
            stream_date = self.when.strftime("%Y-%m-%d")
        else:
            stream_date = "No Date Set"
        return "{} ({}) [#{}]".format(self.title, stream_date, self.pk)


class Stream_Entry(BaseModel):
    model_name = "Stream Entry"
    to_init = ["zfile"]

    zfile = models.ForeignKey("museum_site.File", on_delete=models.SET_NULL, blank=True, null=True)
    title_override = models.CharField(max_length=120, blank=True, help_text="Title used instead of ZFile title")
    author_override = models.CharField(max_length=120, blank=True, help_text="Author used instead of ZFile author")
    company_override = models.CharField(max_length=120, blank=True, help_text="Company used instead of ZFile company")
    release_date_override = models.CharField(max_length=20, blank=True, help_text="Release Date used instead of ZFile release date")
    preview_image_override = models.CharField(max_length=120, blank=True, help_text="Preview Image used instead of ZFile preview image")

    def url(self): return ""

    def get_absolute_url(self): return ""

    def __str__(self):
        if self.zfile is None:
            return "{} [SE#{}]".format(self.title_override, self.pk)
        else:
            return "{} [SE#{}]".format(self.zfile.title, self.pk)

    def get_field_view(self, view="stream"):
        if self.title_override:
            return {"label": "Title", "value": "<a>{}</a>".format(self.title_override), "safe": True}
        return self.zfile.get_field_view(view="title")

    def get_field_authors(self, view="stream"):
        if self.author_override:
            return {"label": "Author", "value": "<a>{}</a>".format(self.author_override), "safe": True}
        return self.zfile.get_field_authors()

    def get_field_companies(self, view="stream"):
        if self.company_override:
            return {"label": "Company", "value": "<a>{}</a>".format(self.company_override), "safe": True}
        return self.zfile.get_field_companies()

    def get_field_zfile_date(self, view="stream"):
        if self.release_date_override:
            return {"label": "Released", "value": "<a>{}</a>".format(self.release_date_override), "safe": True}
        return self.zfile.get_field_zfile_date()

    def preview_url(self):
        if self.preview_image_override:
            return self.preview_image_override
        return self.zfile.preview_url()

    def context_stream(self, view="stream"):
        """ Context to display object during stream overviews """
        context = self.context_universal()
        fields = ["authors", "companies", "zfile_date"]

        context["fields"] = []
        for field in fields:
            field_info = self.get_field(field)
            if field_info.get("label") == "Company" and field_info.get("value") == "":
                continue
            context["fields"].append(field_info)

        return context

    def _init_zfile(self):
        if self.zfile:
            self.zfile.init_model_block_context("detailed", self.request, self.show_staff)

    def as_json(self):
        if not self.zfile:
            return {}
        output = {
            "pk": self.pk,
            "title": self.get_field_view(view="stream"),
            "authors": self.get_field_authors(view="stream"),
            "companies": self.get_field_companies(view="stream"),
            "date": self.get_field_zfile_date(view="stream"),
        }
        return output
