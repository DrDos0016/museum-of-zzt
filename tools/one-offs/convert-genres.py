import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

def main():
    print("This script will convert the SSV field file.genre to proper Genre object associations")
    input("Press Enter to begin... ")

    qs = File.objects.all().order_by("id")

    for f in qs:
        old_genres = f.genre.split("/")
        count = len(old_genres)

        for g in old_genres:
            g = Genre.objects.get(title=g)
            f.genres.add(g)

        if len(f.genres.all()) != count:
            print("UH OH", f.title)

        print(f.title, len(f.genres.all()), count)
    return True


if __name__ == '__main__':
    main()
