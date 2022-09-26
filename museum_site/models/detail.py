from django.db import models
from django.template.defaultfilters import slugify

from museum_site.models.base import BaseModel
from museum_site.core.detail_identifiers import *
from museum_site.querysets.detail_querysets import *


class Detail(BaseModel):
    CATEGORY_CHOICES = [
        ("ZZT", "ZZT"),
        ("SZZT", "Super ZZT"),
        ("Media", "Media"),
        ("Other", "Other"),
        ("Hidden", "Hidden"),
    ]

    model_name = "Detail"
    title = models.CharField(max_length=20)
    description = models.TextField(default="")
    visible = models.BooleanField(default=True)
    slug = models.SlugField(max_length=20, editable=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="Other")

    objects = Detail_Queryset.as_manager()

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title

    def url(self):
        return "/detail/view/{}/".format(self.slug)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Detail, self).save(*args, **kwargs)
