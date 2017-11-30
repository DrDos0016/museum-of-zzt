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
    for file in File.objects.all().order_by("letter", "title"):
        file.save()
        if file.sort_title != file.title.lower():
            print(file, "|", file.sort_title)
    return True

if __name__ == "__main__":
    main()
