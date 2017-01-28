import glob
import os
import sys

from datetime import date

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import Article
from comic.models import Comic


def main():
    files = glob.glob(
        "/var/projects/museum/comic/static/comic/ubgs/*.gif"
    )
    files.sort()
    count = 1

    titles = []


    print(len(files))
    for file in files:
        """
        print("="*40)
        print(file)
        base = os.path.basename(file)
        year = int(base[:4])
        month = int(base[5:7])
        day = int(base[8:10])
        print(year, month, day)
        """


        comic = Comic()

        comic.title = "UBGS #" + str(count)
        comic.comic_id = count
        comic.comic_account = "ubgs"
        # comic.date = date(year, month, day)
        comic.transcript = "-"

        comic.save()
        print(comic)
        count += 1
    return True

if __name__ == "__main__":
    main()
