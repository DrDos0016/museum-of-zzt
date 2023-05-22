import glob
import os
import sys
import time
import requests

import django

django.setup()

from museum_site.models import File  # noqa: E402


def main():
    print("Checks all files for valid archive.org links")
    starting_pk = input("Starting PK (def. 0): ")
    delay = input("Delay between hits in seconds (def. 5s): ")

    starting_pk = 0 if starting_pk == "" else int(starting_pk)
    delay = 5 if delay == "" else int(delay)


    for f in File.objects.filter(pk__gte=starting_pk).order_by("id"):
        if f.archive_name:
            resp = requests.head("https://archive.org/embed/" + f.archive_name)
            if resp.status_code != 200:
                print("{} #{} `{}`".format(resp.status_code, f.id, f.title))
            if delay:
                time.sleep(delay)
        if f.pk % 100 == 0:
            print(f.pk)
    return True


if __name__ == "__main__":
    main()
