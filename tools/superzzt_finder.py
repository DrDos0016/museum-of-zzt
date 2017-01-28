import glob
import os
import sys
import urllib.request

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import File


def main():
    print("Super ZZT World Finder")
    # Iterate over File objects
    # Finds Files() that have no Zips

    count = 0
    for file in File.objects.all().order_by("letter", "filename"):
        file_path = "/var/projects/museum" + file.download_url()


    return True

if __name__ == "__main__":
    main()
