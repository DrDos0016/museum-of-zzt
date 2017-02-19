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

    # Iterate over File objects
    # Finds Files() that have no Zips
    zip_ignore = [904, 2095, 2137]  # Known missing zips
    zip_ignore = []
    print("Finding File objects with missing Zip files:")

    count = 0
    for file in File.objects.all().order_by("letter", "filename"):
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
        if exists == 0 and letter != "extra":  # Ignore anything in extra
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

    # Test URLs
    # Find 404s
    print("Finding viewer URLs which result in error:")

    count = 0
    for file in File.objects.all().order_by("letter", "filename"):
        dl_url = file_path = "http://django.pi:8000" + file.file_url()
        try:
            urllib.request.urlopen(dl_url)
        except urllib.error.HTTPError as e:
            if (dl_url not in skipped_urls):
                print(dl_url)
                count += 1
    print(count, "INVALID URLS")
    print(len(skipped_urls), "SKIPPED.")

    return True

if __name__ == "__main__":
    main()
