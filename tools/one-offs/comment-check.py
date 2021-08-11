import os
import sys
import zipfile

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402
from museum_site.constants import *  # noqa: E402


def main():
    print(
        "This script will print any zip file comments in zips which have them."
    )
    print("Starting...")
    unknown_extensions = {}
    qs = File.objects.all().order_by("id")
    print("Iterating...")

    c_count = 0
    for zgame in qs:
        if os.path.isfile(zgame.phys_path()) and zgame.filename.lower().endswith(".zip"):
            # Examine the zip
            zf = zipfile.ZipFile(zgame.phys_path())
            if zf.comment:
                c_count += 1
                print(zgame.id, zgame.title)
                print(zf.comment)
                print("="*80)

    print("COMMENTS", c_count)

    return True


if __name__ == '__main__':
    main()
