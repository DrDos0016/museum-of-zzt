import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("This script will add Download object entries for all Museum hosted worlds.")
    print("THIS WILL MAKE DB CHANGES")
    input("Press ENTER to begin.")

    qs = File.objects.all().order_by("id")
    for zf in qs:
        if zf.file_exists():
            d_check = Download.objects.filter(url=zf.download_url()).count()
            if d_check:
                #print("SKIP", zf.id, zf)
                continue
            d = Download(url=zf.download_url(), kind="zgames")

            d.save()
            zf.downloads.add(d)
            print(zf.id, zf)
    return True


if __name__ == '__main__':
    main()
