import csv
import os
import sys

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File, Article


def main():
    with open("data/youtube_template.html") as fh:
        TEMPLATE = fh.read()

    with open("data/streams.csv") as fh:
        data = csv.reader(fh, delimiter=",")

        for row in data:
            row[1] = row[1].strip()
            text = TEMPLATE.format(row[0], row[1], row[2])
            date = row[3]
            games = row[4]
            a = Article()

            print(row)

            a.title = "Livestream - " + row[1]
            a.author="Dr. Dos"
            a.category="Livestream"
            a.content = text
            a.type="django"
            a.date = date
            a.published = True
            a.allow_comments = True
            a.save()


            for pk in games.split("/"):
                f = File.objects.get(pk=int(pk))
                f.articles.add(a)
                f.save()
                print("Associated with", f)

    print("DONE")

if __name__ == "__main__":
    main()
