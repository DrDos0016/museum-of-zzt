import datetime
import json
import os
import shutil
import subprocess
import sys
import zipfile

import django

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *

def main():
    DEFAULT_DIR = "/var/projects/museum/private/bulk_uploads"
    DEFAULT_JSON = "/var/projects/museum/tools/games.json"

    print("MUSEUM OF ZZT BULK UPLOAD SCRIPT")
    print("UPDATED 2017-07-27")
    print("-" * 40)

    # Dump from z2's games table to a JSON file, remove the SQL comments
    # Download the zips somewhere
    # Run this

    zip_directory = input("Enter Zip Directory ({})".format(DEFAULT_DIR))
    json_path = input("Enter JSON filepath ({})".format(DEFAULT_JSON))

    if zip_directory == "":
        zip_directory = DEFAULT_DIR
    if json_path == "":
        json_path = DEFAULT_JSON

    with open(json_path) as fh:
        raw = fh.read()
        data = json.loads(raw)
        # z2 keys -- title, author, filenameurl, filenamenice, genre, type,
        # isfg, size
        count = 1
        for z2_file in data:
            if z2_file["filenamenice"] == "RUINS.zip":
                continue
            f = File()
            path = os.path.join(zip_directory, z2_file["filenamenice"])

            """
            {"title":"3D Skull Engine",
            "author":"Aplsos",
            "filenamenice":"3dskull.zip",
            "filenameurl":"zgames\/1num\/3dskull.zip",
            "size":"4",
            "genre":"Engine",
            "isfg":"0",
            "type":"0"}
            """

            # First handle the easy stuff
            lower_title = z2_file["title"].lower()
            if lower_title.startswith("a ") or lower_title.startswith("an ") or lower_title.startswith("the "):
                no_article_title = " ".join(z2_file["title"].split(" ")[1:])
            else:
                no_article_title = z2_file["title"]
            f.letter = no_article_title[0].lower()
            if f.letter not in "abcdefghijklmnopqrstuvwxyz":
                f.letter = "1"

            f.filename = str(z2_file["filenamenice"])
            f.title = z2_file["title"]
            # sort_title handled by saving
            f.author = z2_file["author"]
            f.size = int(os.stat(path).st_size / 1024)
            f.release_date = "2018-01-01"
            f.release_source = ""
            f.company = ""
            f.description = ""
            f.genre = z2_file["genre"]

            # DEBUG -- REMOVE THIS FOR LAUNCH WHEN THIS FIELD IS REMOVED
            f.category = "ZZT"

            # SCREENSHOT -- Currently manual
            # DETAILS -- Currently manual

            # Check for a duplicate filename
            exists = File.objects.filter(filename=f.filename).exists()
            if exists:
                print("ERROR -- The chosen filename is already in use.")

            # md5 checksum
            resp = subprocess.run(["md5sum", path], stdout=subprocess.PIPE)
            md5 = resp.stdout[:32].decode("utf-8")
            f.checksum = md5

            # done
            f.save()
            # move file
            shutil.move(path, "/var/projects/museum/zgames/"+f.letter+"/"+f.filename)
            print(count, f)

            count += 1

    return True

if __name__ == "__main__": main()
