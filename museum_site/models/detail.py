from django.db import models
from django.template.defaultfilters import slugify

from museum_site.models.base import BaseModel
from museum_site.core.detail_identifiers import *


class DetailManager(models.Manager):
    def advanced_search_categories(self):
        os_details = [
            DETAIL_DOS, DETAIL_WIN16, DETAIL_WIN32, DETAIL_WIN64, DETAIL_OSX,
            DETAIL_LINUX
        ]
        qs = self.exclude(pk=DETAIL_REMOVED)
        cats = []

        for d in qs:
            if d.title.startswith("ZZT "):
                cats.append({"priority": 10, "header": "ZZT", "d": d})
            elif d.title.startswith("Super ZZT "):
                cats.append({"priority": 20, "header": "Super ZZT", "d": d})
            elif (
                d.title in [
                    "Image", "Video", "Audio", "Text", "ZZM Audio",
                    "HTML Document"
                ]
            ):  # Media
                cats.append({"priority": 30, "header": "Media", "d": d})
            elif d.id in os_details:
                cats.append({"priority": 90, "header": "OS", "d": d})
            else:
                cats.append({"priority": 80, "header": "Other", "d": d})

        cats.sort(key=lambda k: k["priority"])
        return cats


    def form_list(self):
        os_details = [
            DETAIL_DOS, DETAIL_WIN16, DETAIL_WIN32, DETAIL_WIN64, DETAIL_OSX,
            DETAIL_LINUX
        ]
        qs = self.all()

        output = []
        for d in qs:
            output.append((str(d.id), d.title))

        return output

class Detail(BaseModel):
    CATEGORY_CHOICES = [
        ("ZZT", "ZZT"),
        ("SZZT", "Super ZZT"),
        ("Media", "Media"),
        ("Other", "Other"),
    ]

    model_name = "Detail"
    title = models.CharField(max_length=20)
    description = models.TextField(default="")
    visible = models.BooleanField(default=True)
    slug = models.SlugField(max_length=20, editable=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="Other")

    objects = DetailManager()

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title


    def url(self):
        return "/detail/{}/".format(self.slug)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Detail, self).save(*args, **kwargs)
