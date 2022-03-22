import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    all = Review.objects.all().order_by("id")

    for r in all:
        #print(r.id, end="")
        text = r.content
        qs = Review.objects.filter(content=text).order_by("id")
        dupes = len(qs)
        if dupes > 1:
            print(r.zfile.title, end="")
            for d in qs:
                print(" " + str(d.id), end="")
            print("")
    return True


if __name__ == '__main__':
    main()
