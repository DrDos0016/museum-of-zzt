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

    def screenshot_url(self):
        if self.screenshot and self.screenshot not in self.SPECIAL_SCREENSHOTS:
            return "images/screenshots/{}/{}".format(self.letter, self.screenshot)
        elif self.screenshot:  # Special case
            return "images/screenshots/{}".format(self.screenshot)
        else:
            return "images/screenshots/no_screenshot.png"

    def view_url(self):
        return "/file/view/{}/".format(self.key)
