import os
import subprocess
import sys

import django

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File
from museum_site.common import SITE_ROOT


def main():
    for file in File.objects.all().order_by("id"):
        #print(file)

        resp = subprocess.run(["md5sum", os.path.join(SITE_ROOT, "zgames/") + file.letter + "/" + file.filename], stdout=subprocess.PIPE)
        md5 = resp.stdout[:32].decode("utf-8")
        if file.checksum != md5:
            print("MISMATCH FOR", file)
            print("GOT     :", md5)
            print("EXPECTED:", file.checksum)
    return True

if __name__ == "__main__":
    main()
