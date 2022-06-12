import os
import sys

import django

from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402
from museum_site.core.detail_identifiers import *


def main():
    print("This script will look through any published Files without the NEW_FIND detail and retroactively add it if the release year is not within six months of publication")
    input("Press ENTER to begin.")
    print("Resetting...")

    qs = File.objects.filter(details=DETAIL_NEW_FIND)
    for f in qs:
        f.details.remove(DETAIL_NEW_FIND)
    print("RESET")
    input("")

    delta = timedelta(days=180)

    qs = File.objects.exclude(details__in=[DETAIL_NEW_FIND, DETAIL_UPLOADED]).order_by("-id")
    qs = qs.prefetch_related("upload_set").distinct()
    for f in qs:


        mark_new_find = False
        upload = f.upload_set.first()
        print(f)
        print("RELEASED:", f.release_date)
        print("UPLOADED:", upload.date)

        if upload.date.year <= 2018:
            continue

        if not f.release_date:
            # Assume unknown release dates are new finds for the purpose of this script
            f.details.add(DETAIL_NEW_FIND)
            continue

        diff = f.release_date + delta

        if str(diff)[:10] < str(upload.date)[:10]:
            print("NEW FIND!")
            mark_new_find = True

        if mark_new_find:
            f.details.add(DETAIL_NEW_FIND)




    return True


if __name__ == '__main__':
    main()
