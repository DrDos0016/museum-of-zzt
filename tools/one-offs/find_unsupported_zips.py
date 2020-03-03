"""
Finds zip files that use Implode compression
"""

import glob
import os
import sys
import zipfile

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File, Detail
from museum_site.common import DETAIL_LOST, SITE_ROOT


def main():
    for f in File.objects.all().exclude(details__in=[DETAIL_LOST]).order_by("letter", "filename"):
        if os.path.isfile(f.phys_path()):
            if ".zip" in f.phys_path().lower():
                zip_file = zipfile.ZipFile(f.phys_path())
                info = zip_file.infolist()
                for i in info:
                    if i.compress_type not in [0, 8]:
                        print(f, "\n", i.compress_type, i.filename)

    return True

if __name__ == "__main__":
    main()
