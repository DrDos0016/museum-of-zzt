import glob
import os
import subprocess
import sys
import urllib.request

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from auditor.models import *


def get_md5(file_path):
    """ Return the md5 checksum of a file """
    resp = subprocess.run(["md5sum", file_path], stdout=subprocess.PIPE)
    checksum = resp.stdout[:32].decode("utf-8")
    return checksum


def main():
    print("File Identifier -- Input a path with a bunch of ZZT files via commandline")
    path = sys.argv[-1]
    results = []

    file_list = glob.glob(path + "/*.*")

    for file in file_list:
        md5 = get_md5(file)
        size = os.path.getsize(file)
        name = os.path.basename(file)

        no_md5 = False
        no_name = False
        no_size = False

        # Queries
        md5_matches = Entry.objects.filter(md5=md5)
        name_matches = Entry.objects.filter(filename=name)
        size_matches = Entry.objects.filter(size=size)

        if md5_matches:
            for entry in md5_matches:
                print(name, "shares md5 with", entry.filename, "from", entry.origin.filename, ':', entry.origin.title)
        else:
            no_md5 = True

        if name_matches:
            for entry in name_matches:
                print(name, "shares name with", entry.filename, "from", entry.origin.filename, ':', entry.origin.title)
        else:
            no_name = True

        if size_matches:
            for entry in name_matches:
                print(name, "shares file size with", entry.filename, "from", entry.origin.filename, ':', entry.origin.title)
        else:
            no_size = True

        if no_md5 and no_name and no_size:
            print(name, "IS COMPLETELY UNIQUE")

if __name__ == "__main__":
    main()
