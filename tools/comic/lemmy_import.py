import glob
import os
import sys

from datetime import date

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from comic.models import Comic


def main():
    files = glob.glob(
        "/var/projects/museum/comic/static/comic/lemmy/*.jpg"
    )
    files.sort()

    count = 1
    for file in files:
        base = os.path.basename(file).replace("lemmy", "").replace(".jpg", "")
        year = int(base[:4])
        month = int(base[4:6])
        day = int(base[6:])
        print("YMD", year, month, day)
        """
            title = models.CharField(max_length=100)
        comic_id = models.IntegerField()
        comic_account = models.CharField(
            max_length=10, choices=ACCOUNTS
        )
        date = models.DateField(null=True, blank=True, default=None)
        transcript = models.TextField()
        characters = models.ManyToManyField("Character")
        """

        comic = Comic()
        comic.title = "Lemmy Comics #" + str(count)
        comic.comic_id = count
        comic.comic_account = "lemmy"
        comic.date = date(year, month, day)
        comic.transcript = "-"

        comic.save()
        print(comic)
        count += 1
    return True

if __name__ == "__main__":
    main()
