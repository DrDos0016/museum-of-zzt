import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    qs = Review.objects.all().order_by("id")
    for r in qs:
        print(str(r.id) + "|" + str(r.date))
    return True


if __name__ == '__main__':
    main()
