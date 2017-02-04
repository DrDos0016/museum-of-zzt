import os
import subprocess
import sys


import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import File


def main():
    for file in File.objects.all().order_by("letter", "filename"):
        file_path = "/var/projects/museum" + file.download_url()
        if not os.path.isfile(file_path):
            # Files which don't exist are handled by audit.py
            continue

        # Get the md5 checksum
        resp = subprocess.run(["md5sum", file_path], stdout=subprocess.PIPE)
        md5 = resp.stdout[:32].decode("utf-8")
        file.checksum = md5
        file.save()
        print(file_path)

    return True

if __name__ == "__main__":
    main()
