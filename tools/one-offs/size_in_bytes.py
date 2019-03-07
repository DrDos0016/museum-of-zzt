import glob
import os
import sys
import urllib.request

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File, Detail
from museum_site.common import DETAIL_LOST


def main():
    qs = File.objects.exclude(details__in=[DETAIL_LOST]).order_by("id")

    for f in qs:
        if f.id == 2320:
            print("Skipping AOL")
            continue
        f.calculate_size()
        f.save()
        print(f.size, f)


if __name__ == "__main__":
    main()
