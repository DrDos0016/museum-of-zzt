import glob
import os
import sys
import requests

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File

def main():
    print("Checks all files for valid archive.org links")
    input("Press enter to continue")
    for f in File.objects.all().order_by("id"):
        if f.archive_name:
            resp = requests.get("https://archive.org/embed/" + f.archive_name)
            if resp.status_code != 200:
                print(resp.status_code, f.id, f.title)
        else:
            print(f, "has no value for archive_name")
    return True

if __name__ == "__main__":
    main()

