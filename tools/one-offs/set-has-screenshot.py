import glob
import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.constants import STATIC_PATH
from museum_site.models import *  # noqa: E402


def main():

    rename = input("Rename existing screenshots to lowercase? (1=Yes) ")
    if rename == "1":
        print("Renaming...")
        existing = glob.glob(os.path.join(STATIC_PATH, "screenshots/*/*.png"))
        sorted(existing)
        seen = []
        for image in existing:
            filename = os.path.basename(image)
            """
            if filename not in seen:
                seen.append(filename)
            else:
                print("DUPLICATE KEY", filename)
            """
            cmd = "mv {} {}".format(image, image.lower())
            os.system(cmd)
        print("Renamed! {}".format(len(existing)))



    qs = File.objects.filter(has_preview_image=False)

    for zf in qs:
        preview_image_path = os.path.join(STATIC_PATH, "screenshots/{}/{}".format(zf.bucket(), zf.key + ".png"))
        if os.path.isfile(preview_image_path):
            zf.has_preview_image = True
            zf.save()
        else:
            print("NO PREVIEW IMAGE FOR:", zf)
    return True


if __name__ == '__main__':
    main()
