import os
import sys
import urllib

import django
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    # Detects files which cannot be displayed by the file viewer
    qs = File.objects.all().prefetch_related("content").order_by("id")

    count = 0
    for f in qs:
        for c in f.content.all():
            #http://django.pi:8000/ajax/get_zip_file/?letter=m&zip=macgyver.zip&filename=macgyver.txt&format=auto&uploaded=false
            url = "http://django.pi:8000/ajax/get_zip_file/?letter={}&zip={}&filename={}&format=auto&uploaded=false".format(
                f.letter, urllib.parse.quote(f.filename), urllib.parse.quote(c.path)
            )
            r = requests.get(url)
            if r.status_code != 200:
                print(f)
                print(r.status_code, c.title, r.headers.get("content-length"), "bytes", url)
        count += 1
        if count % 100 == 0:
            print(count, "Files anaylzed")


    return True


if __name__ == '__main__':
    main()
