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

    zfile = models.ForeignKey("museum_site.File", on_delete=models.SET_NULL, blank=True, null=True)
    title_override = models.CharField(max_length=120, blank=True, help_text="Title used instead of ZFile title")
    author_override = models.CharField(max_length=120, blank=True, help_text="Author used instead of ZFile author")
    company_override = models.CharField(max_length=120, blank=True, help_text="Company used instead of ZFile company")
    release_date_override = models.CharField(max_length=20, blank=True, help_text="Release Date used instead of ZFile release date")
    preview_image_override = models.CharField(max_length=120, blank=True, help_text="Preview Image used instead of ZFile preview image")

    def __str__(self):
        if self.zfile is None:
            return "{} [SE#{}]".format(self.title_override, self.pk)
        else:
            return "{} [SE#{}]".format(self.zfile.title, self.pk)

    def get_title(self):
        if self.zfile:
            return self.zfile.title
        return self.title_override

    def get_author(self):
        if self.zfile:
            return self.zfile.get_field_authors()
        return self.author_override

    def get_company(self):
        if self.zfile:
            return self.zfile.get_field_companies()
        return self.company_override

    def get_author(self):
        if self.zfile:
            return self.zfile.get_field_zfile_date
        return self.title_override
