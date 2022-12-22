import os

from museum.settings import STATIC_URL
from museum_site.core.detail_identifiers import *


class ZFile_Urls:
    def article_url(self):
        return "/file/article/{}/".format(self.key)

    def attributes_url(self):
        return "/file/attribute/{}/".format(self.key)

    def download_url(self):
        if (not self.id) or self.is_detail(DETAIL_UPLOADED):
            return "/zgames/uploaded/{}".format(self.filename)
        else:
            return "/zgames/{}/{}".format(self.letter, self.filename)

    def play_url(self):
        return "/file/play/{}/".format(self.key)

    def review_url(self):
        return "/file/review/{}/".format(self.key)

    def tool_url(self):
        return "/tools/{}/".format(self.key)

    def preview_url(self):
        if self.screenshot:
            if self.screenshot not in self.SPECIAL_SCREENSHOTS:
                return os.path.join("images/screenshots/{}/{}".format(self.letter, self.screenshot))
            else:
                return os.path.join("images/screenshots/{}".format(self.screenshot))
        return os.path.join("images/screenshots/no_screenshot.png")

    def url(self):
        return "/file/view/{}/".format(self.key)

    def view_url(self):
        return self.url()
