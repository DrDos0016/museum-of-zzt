import os

from django.urls import reverse

from museum.settings import STATIC_URL
from museum_site.core.detail_identifiers import *


class ZFile_Urls:
    def article_url(self):
        return reverse("article", kwargs={"key": self.key})

    def attributes_url(self):
        return reverse("file_attributes", kwargs={"key": self.key})

    def download_url(self):
        try:
            zgame = self.downloads.filter(kind="zgames").first()
            if zgame:
                return zgame.get_absolute_url()
        except ValueError:
            return "X"
        return "#"

    def get_absolute_url(self):
        return reverse("file", kwargs={"key": self.key})

    def play_url(self):
        return reverse("play", kwargs={"key": self.key})

    def review_url(self):
        return reverse("reviews", kwargs={"key": self.key})

    def tool_url(self):
        return reverse("tool_index_with_file", kwargs={"key": self.key})

    def preview_url(self):
        if self.has_preview_image:
            return os.path.join("screenshots/{}/{}.png".format(self.bucket(), self.key))
        else:
            if self.is_detail(DETAIL_ZZM):
                return os.path.join("screenshots/zzm_screenshot.png")
            return os.path.join("screenshots/no_screenshot.png")
