import django
import os
import re
import sys
import zipfile

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from museum_site.models import File


def main():
    shortcuts = {
        "1":"(.*).[zZ][zZ][tT]$",
        "2":"(.*).[sS][zZ][tT]$",
        "3":"(.*).[zZ][iI][gG]$",
        "4":"(.*).[zZ][zZ][mM]$",
        "5":"(.*).[tT][xX][tT]$",
        "6":"(.*).[dD][oO][cC]$",
        "7":"(.*).[bB][rR][dD]$",
        "8":"(.*).[eE][xX][eE]$",
    }
    print("SHORTCUTS")
    for x in range(1,9):
        print(x, shortcuts[str(x)])

    contains_regex = input("Regex to list Files that do match: ")
    if contains_regex in shortcuts.keys():
        contains_regex = shortcuts[contains_regex]

    lacks_regex = input("Regex to list Files that don't match: ")
    if lacks_regex in shortcuts.keys():
        lacks_regex = shortcuts[lacks_regex]

    files = File.objects.all().order_by("letter", "title")
    lacks_matches = ""
    contains_matches = ""
    for f in files:
        letter = f.letter
        zip = f.filename

        # Open the zip
        try:
            zip = zipfile.ZipFile(
                "/var/projects/museum/zgames/" + letter + "/" + zip
            )
        except Exception as e:
            # The audit script should handle missing/invalid zips, not this.
            continue

        # Print files
        lack_fail = False
        try:
            file_list = zip.namelist()

            for file in file_list:
                if contains_regex:
                    if (re.match(contains_regex, file)):
                        contains_matches += str(f.id)+","
                        print("+", f.id, f.title)
                if lacks_regex:
                    if (re.match(contains_regex, file)):
                        lack_fail = True
        except:
            continue

        if lacks_regex and lack_fail:
            lack_matches += str(f.id)+","
            print("-", f.id, f.title)

    print(contains_matches)
    print(lacks_matches)
    return True

if __name__ == "__main__":
    main()
