import django
import os
import re
import sys
import zipfile

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File  # noqa: E402
from museum_site.constants import SITE_ROOT  # noqa: E402


def main():
    shortcuts = {
        "1": "(.*).[zZ][zZ][tT]$",
        "2": "(.*).[sS][zZ][tT]$",
        "3": "(.*).[zZ][iI][gG]$",
        "4": "(.*).[zZ][zZ][mM]$",
        "5": "(.*).[tT][xX][tT]$",
        "6": "(.*).[dD][oO][cC]$",
        "7": "(.*).[bB][rR][dD]$",
        "8": "(.*).[eE][xX][eE]$",
        "9": "(.*).[cC][oO][mM]$",
    }
    length = len(list(shortcuts.keys()))
    print("SHORTCUTS")
    for x in range(1, length + 1):
        print(x, shortcuts[str(x)])

    contains_regex = input("Regex to list Files that do match: ")
    if contains_regex in shortcuts.keys():
        contains_regex = shortcuts[contains_regex]

    lacks_regex = input("Regex to list Files that don't match: ")
    if lacks_regex in list(shortcuts.keys()):
        lacks_regex = shortcuts[lacks_regex]

    files = File.objects.all().order_by("letter", "title")
    lacks_matches = ""
    contains_matches = ""

    print("LACKS", lacks_regex)

    for f in files:
        letter = f.letter
        fn = f.filename

        # Open the zip
        try:
            zf = zipfile.ZipFile(
                os.path.join(SITE_ROOT, "zgames", (letter + "/" + fn))
            )
        except Exception as e:
            # The audit script should handle missing/invalid zips, not this.
            print(e)
            continue

        # Print files
        lack_fail = False
        try:
            file_list = zf.namelist()

            for zfn in file_list:
                if contains_regex:
                    if (re.match(contains_regex, zfn)):
                        print(fn, zfn)
                if lacks_regex:
                    if (not re.match(lacks_regex, zfn)):
                        print(fn, zfn)
        except Exception as e:
            print(e)
            continue
    return True


if __name__ == "__main__":
    main()
