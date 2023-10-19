import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("This script will move the values of zfile.checksum and zfile.size to download.checksum and download.size for the 'Zgame' download.")
    input("Press ENTER to begin.")

    qs = File.objects.all().order_by("pk")
    for zf in qs:
        dl = zf.downloads.filter(kind="zgames").first()
        if dl:
            dl.size = zf.size
            dl.checksum = zf.checksum
            dl.save()
            print("Updated", zf)
        else:
            print("zgames download not found for", zf)

    return True


if __name__ == '__main__':
    main()
