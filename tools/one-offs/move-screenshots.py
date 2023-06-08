import os
import shutil
import sys

import django

django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.core.detail_identifiers import *
from museum_site.constants import STATIC_PATH, PREVIEW_IMAGE_BASE_PATH
from museum_site.models import *  # noqa: E402


def main():
    old_screenshot_root = os.path.join(STATIC_PATH, "images", "screenshots")
    qs = File.objects.exclude(screenshot="").order_by("id")
    for zf in qs:
        if zf.screenshot.startswith("zzm_screenshoot"):
            continue

        try:
            src = os.path.join(old_screenshot_root, zf.letter, zf.screenshot)
            dst = os.path.join(PREVIEW_IMAGE_BASE_PATH, zf.bucket(), zf.screenshot)
            shutil.move(src, dst)
        except FileNotFoundError:
            print("COULD NOT MOVE", src)
    return True


if __name__ == '__main__':
    main()
