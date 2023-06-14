import os

from museum.settings import STATIC_URL
from museum_site.core.detail_identifiers import *


class ZFile_Urls:
    def article_url(self):
        return "/file/article/{}/".format(self.key)

    def attributes_url(self):
        return "/file/attribute/{}/".format(self.key)

    def download_url(self):
        zgame = self.downloads.filter(kind="zgames").first()
        if zgame:
            return zgame.url
        return "#"

    def play_url(self):
        return "/file/play/{}/".format(self.key)

    def review_url(self):
        return "/file/review/{}/".format(self.key)

    def tool_url(self):
        return "/tools/{}/".format(self.key)

    def preview_url(self):
        if self.screenshot:
            if self.screenshot not in self.SPECIAL_SCREENSHOTS:
                return os.path.join("screenshots/{}/{}".format(self.bucket(), self.screenshot))
            else:
                return os.path.join("screenshots/{}".format(self.screenshot))
        return os.path.join("screenshots/no_screenshot.png")

    def url(self):
        return "/file/view/{}/".format(self.key)

    def view_url(self):
        return self.url()
