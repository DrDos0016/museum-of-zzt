import glob
import os
import sys
import urllib.request

import django
django.setup()

from museum_site.models import File, Detail  # noqa: E402
from museum_site.common import DETAIL_LOST  # noqa: E402


def main():
    skipped_urls = []

    # Iterate over Zips
    # Find zips without Files()
    print("Finding Zip files with no associated File object:")
    zips = glob.glob("/var/projects/museum/zgames/**/*.zip")
    count = 0
    files_ignore = 0
    for zip in zips:
        letter, filename = zip.replace(
            "/var/projects/museum/zgames/", ""
        ).split("/")
        exists = File.objects.filter(letter=letter, filename=filename).count()
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
    for f in File.objects.all().order_by("letter", "filename"):
        if f.details.all().count() == 0:
            no_details_count += 1
            print(f, "has no details!")
    print(no_details_count, "files without details.")

    # Test URLs
    # Find 404s
    print("Finding viewer URLs which result in error:")
    lost = Detail.objects.get(pk=DETAIL_LOST)
    count = 0
    for f in File.objects.all().order_by("letter", "filename"):
        url = "http://django.pi:8000" + urllib.parse.quote(f.file_url())
        try:
            urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            if (lost not in f.details.all()):
                print(url)
                count += 1
    print(count, "INVALID URLS")
    print(len(skipped_urls), "SKIPPED.")

    return True


if __name__ == "__main__":
    main()
