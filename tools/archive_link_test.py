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
    for f in File.objects.all().order_by("id"):
        resp = requests.get("https://archive.org/embed/" + f.archive_name)
        if resp.status_code != 200:
            print(resp.status_code, f.id, f.title)
    return True

if __name__ == "__main__":
    main()

