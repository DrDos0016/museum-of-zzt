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
    # Iterate over File objects
    # Finds Files() that have no Zips
    print("Finding File objects with missing Zip files:")

    count = 0
    for file in File.objects.all().order_by("letter", "filename"):
        file_path = "/var/projects/museum" + file.download_url()
        if not os.path.isfile(file_path):
            print(str(file.id).zfill(4), file.letter, file.filename)
            count += 1

    print(count, "MISSING ZIPS")
    print("="*40)

    # Iterate over Zips
    # Find zips without Files()
    print("Finding Zip files with no associated File object:")
    zips = glob.glob("/var/projects/museum/zgames/**/*.zip")
    count = 0
    for zip in zips:
        letter, file = zip.replace("/var/projects/museum/zgames/", "").split("/")
        exists = File.objects.filter(letter=letter, filename=file).count()
        if exists == 0:
            count += 1
            print("Missing entry for", zip)
        elif exists > 1:
            print(exists, "copies of", zip)
            count += 1

    print(count, "MISSING FILES()")
    print("="*40)

    # Test URLs
    # Find 404s
    print("Finding download URLs which result in error:")

    count = 0
    for file in File.objects.all().order_by("letter", "filename"):
        dl_url = file_path = "http://django.pi:8000" + file.file_url()
        try:
            resp = urllib.request.urlopen(dl_url)
        except urllib.error.HTTPError as e:
            print(dl_url)
            count += 1
    print(count, "INVALID URLS")

    return True

if __name__ == "__main__":
    main()
