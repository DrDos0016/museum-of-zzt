from datetime import datetime

from django.db import models

from museum_site.models.base import BaseModel


class Stream(BaseModel):
    model_name = "Stream"

    title = models.CharField(max_length=120)
    description = models.CharField(max_length=300)
    when = models.DateTimeField()
    vod = models.ForeignKey("museum_site.Article", on_delete=models.SET_NULL, blank=True, null=True)
    preview_image = models.CharField(max_length=120, help_text="Preview Image used instead of ZFile preview image")
    entries = models.ManyToManyField("Stream_Entry", default=None, blank=True, help_text="Stream Entries to be played during this stream")
    visible = models.BooleanField(default=True)

    def when_in_pacific(self):
        print(self.when)
        print(self.when.tzinfo)
        return self.when


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

    def __str__(self):
        if self.zfile is None:
            return "{} [SE#{}]".format(self.title_override, self.pk)
        else:
            return "{} [SE#{}]".format(self.zfile.title, self.pk)

    def get_field_view(self, view="stream"):
        if not self.zfile:
            return {"label": "Title", "value": "<a>{}</a>".format(self.title_override), "safe": True}
        return self.zfile.get_field_view(view="title")

    def get_field_authors(self, view="stream"):
        if not self.zfile:
            return {"label": "Author", "value": "<a>{}</a>".format(self.author_override), "safe": True}
        return self.zfile.get_field_authors()

    def get_field_companies(self, view="stream"):
        if not self.zfile:
            return {"label": "Company", "value": "<a>{}</a>".format(self.company_override), "safe": True}
        return self.zfile.get_field_companies()

    def get_field_zfile_date(self, view="stream"):
        if not self.zfile:
            return {"label": "Releasede", "value": "<a>{}</a>".format(self.release_date_override), "safe": True}
        return self.zfile.get_field_zfile_date()

    def preview_url(self):
        if not self.zfile:
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