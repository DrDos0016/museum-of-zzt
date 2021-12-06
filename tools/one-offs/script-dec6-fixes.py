import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("Dec. 6th fixes.")
    print("Running this script will perform 3 actions")
    print("1. Remove 'Non-English' from all Files' genre values")
    print("2. Remove 'Explicit' from all Files' genre values")
    print("3. Recalculate Sort_title on all Files.")

    input("Press Enter to run and make changes to the database")

    qs = File.objects.all()

    for f in qs:
        genre_list = f.genre.split("/")
        new_genres = ""
        for g in genre_list:
            if g not in ["Non-English", "Explicit"]:
                new_genres += g + "/"
            else:
                print(f, "is having its genre modified")
        f.calculate_sort_title()
        new_genres = new_genres[:-1]
        f.genre = new_genres
        f.basic_save()
    return True


if __name__ == '__main__':
    main()
