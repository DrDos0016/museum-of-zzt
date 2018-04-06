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
    with open("broken_archive_links.txt", "w") as fh:
        for f in File.objects.all().order_by("id"):
            resp = requests.get("https://archive.org/embed/zzt_" + f.filename[:-4])
            if resp.status_code != 200:
                print(resp.status_code, f.id, f.title)
                fh.write(str(resp.status_code) + " " + str(f.id) + " " + f.title + "\n")
                f.archive_name = ""
                f.save()
    return True

if __name__ == "__main__":
    main()

