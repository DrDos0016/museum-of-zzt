import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("Running this script will take zfile objects and calculate their feedback and review counts.")
    input("Press Enter to begin")

    qs = File.objects.all()

    for zf in qs:
        zf.calculate_reviews()
        zf.calculate_feedback()
        zf.save()
        print(zf.pk)
    print("DONE.")
    return True


if __name__ == '__main__':
    main()
