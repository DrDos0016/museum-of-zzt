import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402


def main():
    qs = File.objects.all().order_by("id")
    for f in qs:
        z = os.path.splitext(f.filename)[0]
        if f.screenshot:
            s = os.path.splitext(f.screenshot)[0]
        else:
            continue
        if z != s:
            print(f.id, f.title)
            print("\t", f.filename, f.screenshot)
    return True


if __name__ == '__main__':
    main()
