import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("Run to iterate over all files. Those with 'explicit' in their "
          "genre will have the genre removed and file.explicit set to True.")

    print("TODO THIS CANNOT BE RAN UNTIL NEW UPLOAD ALLOWS MARKING WORLDS AS EXPLICIT")
    input("Press Enter to make changes to the database.")

    qs = File.objects.all()
    for f in qs:
        if "Explicit" in f.genre:
            gs = f.genre.split("/")
            gs.remove("Explicit")
            print(f)
            print(gs)
            new_gs = "/".join(gs)
            print(new_gs)
            f.genre = new_gs
            f.save()
    return True


if __name__ == '__main__':
    main()
