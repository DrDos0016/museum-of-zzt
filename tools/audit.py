import glob
import os
import sys
import urllib.request

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File, Detail
from museum_site.common import DETAIL_LOST


def main():

    """
    skipped_urls = [
        "http://django.pi:8000/file/d/Dragon.zip",
        "http://django.pi:8000/file/d/prison.zip",
        "http://django.pi:8000/file/k/kevedit-setup-0.5.0-win32.exe",
        "http://django.pi:8000/file/m/MADTOM3.ZIP",
        "http://django.pi:8000/file/m/mystZZT.zip",
        "http://django.pi:8000/file/r/rings2.zip",
        "http://django.pi:8000/file/s/Bob.zip",
        "http://django.pi:8000/file/z/zztpiano.exe",
    ]
    """
    skipped_urls = []

    # Iterate over File objects
    # Finds Files() that have no Zips (and aren't known Lost Worlds)
    zip_ignore = [904, 2095, 2137]  # Known missing zips
    zip_ignore = []
    print("Finding File objects with missing Zip files:")

    count = 0
    for file in File.objects.all().exclude(details__in=[DETAIL_LOST]).order_by("letter", "filename"):
        file_path = "/var/projects/museum" + file.download_url()
        if not os.path.isfile(file_path):

            if file.id in zip_ignore:
                continue

            print(str(file.id).zfill(4), file.letter, file.filename)
            count += 1

    print(count, "MISSING ZIPS")
    print(len(zip_ignore), "IDs purposely ignored")
    print("=" * 40)

    # Iterate over Zips
    # Find zips without Files()
    print("Finding Zip files with no associated File object:")
    zips = glob.glob("/var/projects/museum/zgames/**/*.zip")
    count = 0
    files_ignore = 0
    for zip in zips:
        letter, file = zip.replace(
            "/var/projects/museum/zgames/", ""
        ).split("/")
        exists = File.objects.filter(letter=letter, filename=file).count()
        # Some zgames folders are excluded deliberately
        if exists == 0 and letter not in ["extra", "mass"]:
            count += 1
            print("Missing entry for", zip)
        elif exists > 1:
            if (exists == 2 and
                    zip in [
                        "/var/projects/museum/zgames/p/pupegold.zip",
                        "/var/projects/museum/zgames/z/palace.zip",
                        "/var/projects/museum/zgames/p/Pirate.zip",
                        "/var/projects/museum/zgames/c/choasdemo2.zip",
                        "/var/projects/museum/zgames/f/Fantasy.zip",
                        "/var/projects/museum/zgames/f/fantasy.zip",
                        "/var/projects/museum/zgames/t/tc.zip",
                        "/var/projects/museum/zgames/t/TC.zip",
                        "/var/projects/museum/zgames/v/village2.zip",
                        "/var/projects/museum/zgames/v/Village.zip",
                        "/var/projects/museum/zgames/v/village.zip",
                        "/var/projects/museum/zgames/v/VILLAGE2.zip",
                    ]):
                files_ignore += 1
                continue
            print(exists, "copies of", zip)
            count += 1

    print(count, "MISSING FILES()")
    print(files_ignore, "Files purposely ignored")
    print("=" * 40)

    # Test files with no details


    print("=" * 40)
    no_details_count = 0
    for file in File.objects.all().order_by("letter", "filename"):
        if file.details.all().count() == 0:
            no_details_count += 1
            print(file, "has no details!")
    print(no_details_count, "files without details.")


    # Test URLs
    # Find 404s
    print("Finding viewer URLs which result in error:")
    lost = Detail.objects.get(pk=DETAIL_LOST)
    count = 0
    for file in File.objects.all().order_by("letter", "filename"):
        dl_url = file_path = "http://django.pi:8000" + file.file_url()
        try:
            urllib.request.urlopen(dl_url)
        except urllib.error.HTTPError as e:
            if (lost not in file.details.all()):
                print(dl_url)
                count += 1
    print(count, "INVALID URLS")
    print(len(skipped_urls), "SKIPPED.")

    return True

if __name__ == "__main__":
    main()
