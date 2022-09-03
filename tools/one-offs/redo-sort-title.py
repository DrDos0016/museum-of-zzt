import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File  # noqa: E402


def main():
    print("Script to recalculate all files' sort titles.")
    print(
        "2022-09-03 - Used to fix inconsistencies in calculations w/ titles"
        " which contained numbers directl followed by a letter rather than a space"
    )
    input("Press ENTER to begin. Database will likely be modified by this process.")
    ogs = []
    revised =[]

    qs = File.objects.all()
    for zf in qs:
        ogs.append(zf.sort_title)
        zf.calculate_sort_title()
        revised.append(zf.sort_title)
        zf.save()

    for x in range(0, len(ogs)):
        if ogs[x] != revised[x]:
            padded = (ogs[x] + (" "* 80))[:80]
            print(padded + " | " + revised[x])
    return True


if __name__ == '__main__':
    main()

