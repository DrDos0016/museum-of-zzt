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
    comics = Comic.objects.filter(comic_account="frost")

    for comic in comics:
        if comic.id in [1015, 1026]:
            continue
        idx = comic.commentary.find("<p")
        print(comic.commentary[idx:idx+70])
        print("$"*50)
        comic.commentary = comic.commentary[idx:]
        comic.save()
    return True

if __name__ == "__main__":
    main()
