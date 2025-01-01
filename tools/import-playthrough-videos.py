import os
import sys

from datetime import datetime

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("This tool takes a list of YouTube URLS and ZFile keys and creates a Playthrough article for that video.")
    print("The article will be public and non-spotlight.")
    input("Press Enter to begin")

    with open("data/playthroughs.txt") as fh:
        for line in fh.readlines():
            (url, key) = line.strip().split(";")
            video_id = url[url.find("=") + 1:url.find("&")]
            zf = File.objects.get(key=key)
            print(video_id, key, zf)

            a  = Article()

            a.title = "Full Playthrough - {}".format(zf.title)
            a.category = "Playthrough"
            a.content = "TODO"
            a.publish_date = datetime.utcnow()
            a.published = Article.PUBLISHED
            a.description = "A complete, commentary free playthrough"
            a.spotlight = False
            a.static_directory = models.CharField("pt-{}".format(zf.key))


    return True


if __name__ == '__main__':
    main()
