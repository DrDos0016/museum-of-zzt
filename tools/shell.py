import glob
import os
import sys
import urllib.request

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import *
from comic.models import *


def main():
    with open("shell.log", "w") as fh:
        command = input(">>> ")
        fh.write(command + "\n")



    return True

if __name__ == "__main__":
    main()
