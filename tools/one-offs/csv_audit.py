import csv
import os
import sys

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import File


def main():
    fh = open("/var/projects/museum/tools/archive.csv")

    data = csv.reader(fh)
    count = 0

    for row in data:
        title = row[0]
        author = row[1]
        filename = row[2]

        # Check if the name is in our DB
        if File.objects.filter(title=title).count() == 0:

            # And is the filename missing as well?
            zname = filename.split("/")[-1]

            if File.objects.filter(filename=zname).count() == 0:
                print("MISSING GAME")
                print("\t", title)
                print("\t", author)
                print("\t", filename)
                count += 1

    print(count, "missing games")

    return True

if __name__ == "__main__":
    main()
