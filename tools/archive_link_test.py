import glob
import os
import sys
import requests

import django

django.setup()

from museum_site.models import File  # noqa: E402


def main():
    print("Checks all files for valid archive.org links")
    input("Press enter to continue")
    for f in File.objects.all().order_by("id"):
        if f.archive_name:
            resp = requests.head("https://archive.org/embed/" + f.archive_name)
            if resp.status_code != 200:
                print("{} #{} `{}`".format(resp.status_code, f.id, f.title))
    return True


if __name__ == "__main__":
    main()
