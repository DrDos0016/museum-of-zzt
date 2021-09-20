from django.db import models

from .constants import (
    DETAIL_REMOVED, DETAIL_DOS, DETAIL_WIN16, DETAIL_WIN32, DETAIL_WIN64,
    DETAIL_OSX, DETAIL_LINUX
)


class DetailManager(models.Manager):
    def advanced_search_categories(self):
        os_details = [
            DETAIL_DOS, DETAIL_WIN16, DETAIL_WIN32, DETAIL_WIN64, DETAIL_OSX,
            DETAIL_LINUX
        ]
        qs = self.exclude(pk=DETAIL_REMOVED)
        cats = []

        for d in qs:
            if d.detail.startswith("ZZT "):
                cats.append({"priority": 10, "header": "ZZT", "d": d})
            elif d.detail.startswith("Super ZZT "):
                cats.append({"priority": 20, "header": "Super ZZT", "d": d})
            elif d.detail in ["Image", "Video", "Audio", "Text", "ZZM Audio", "HTML Document"]:  # Media
                cats.append({"priority": 30, "header": "Media", "d": d})
            elif d.id in os_details:
                cats.append({"priority": 90, "header": "OS", "d": d})
            else:
                cats.append({"priority": 80, "header": "Other", "d": d})

        cats.sort(key=lambda k: k["priority"])
        return cats


class Detail(models.Model):
    detail = models.CharField(max_length=20)
    description = models.TextField(default="")
    visible = models.BooleanField(default=True)

    objects = DetailManager()

    class Meta:
        ordering = ["detail"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.detail
