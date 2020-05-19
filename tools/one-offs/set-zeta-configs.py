import os
import sys
import zipfile

import django

import zookeeper

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402


def main():
    input("This script automatically sets a Zeta Config for all File objects \
without one. Press ENTER to begin.")

    qs = File.objects.filter(zeta_config=None).order_by("id")

    for f in qs:
        if f.is_super_zzt():
            f.zeta_config_id = 4
        if f.is_zzt():
            f.zeta_config_id = 1
        if f.zeta_config_id is not None:
            f.save()
            print("Set config for", f)


if __name__ == '__main__':
    main()
