# This file doesn't care about "don't repeat yourself". Sorry.

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile

import django

from datetime import datetime

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File

from museum_site.constants import (
    DETAIL_ZZT, DETAIL_SZZT, DETAIL_ZIG, DETAIL_UTILITY
)
from museum_site.common import SITE_ROOT

CRON_ROOT = os.path.join(SITE_ROOT, "tools", "crons")

HEADER = """
T H E   M U S E U M   O F   Z Z T   P R E S E N T S

A compiliation of all ZZT worlds released in {} hosted on the Museum of ZZT.

To run:
- Download ZZT v3.2 from https://museumofzzt.com/file/z/zzt.zip
- Extract ZZT and any worlds you wish you play into a directory
- Download the latest version of Zeta from https://zeta.asie.pl
- Extract Zeta into the directory containing ZZT and your ZZT worlds
- Run zeta86.exe and configure ZZT (You'll likely want "K"eyboard and "C"olor)
- Press W to bring up the world list and ENTER to select a world
- Press P to play!

For more detailed instructions, please refer to
https://museumofzzt.com/zeta

{} files are included in this compilation:

"""[1:]

SZZT_HEADER = """
T H E   M U S E U M   O F   Z Z T   P R E S E N T S

A compiliation of all Super ZZT worlds hosted on the Museum of ZZT.

To run:
- Download Super ZZT from https://museumofzzt.com/file/s/szzt.zip
- Download DOSBox from http://www.dosbox.com
- Extract Super ZZT and any worlds you wish you play into a directory
- Mount the directory in DOSBox with the command:
  mount c C:\\path\\to\\Super ZZT\\directory
- Run SZZT.EXE /e and follow the on screen setup instructions (the
  /e flag enables Super ZZT's editor by pressing "E")
- Press W to bring up the world list and ENTER to select a world
- Press P to play!

{} files are included in this compilation:

"""[1:]

ZIG_HEADER = """
T H E   M U S E U M   O F   Z Z T   P R E S E N T S

A compiliation of all ZIG worlds hosted on the Museum of ZZT.

To run:
- Download ZIG v2.1a from https://museumofzzt.com/file/z/zig21a.zip
- Download DOSBox from http://www.dosbox.com
- Extract ZIG and any worlds you wish you play into a directory
- Mount the directory in DOSBox with the command:
  mount c C:\\path\\to\\ZIG\\directory
- Run ZIG.EXE
- Press W to bring up the world list and ENTER to select a world
- Press P to play!

{} files are included in this compilation:

"""[1:]

UTIL_HEADER = """
T H E   M U S E U M   O F   Z Z T   P R E S E N T S

A compiliation of all utilities hosted on the Museum of ZZT.

{} files are included in this compilation:

"""[1:]

FOOTER = """
- https://museumofzzt.com -
"""


def main():
    file_list = {
        "zzt_worlds_UNKNOWN": [],
        "zzt_worlds_1991": [],
        "zzt_worlds_1992": [],
        "zzt_worlds_1993": [],
        "zzt_worlds_1994": [],
        "zzt_worlds_1995": [],
        "zzt_worlds_1996": [],
        "zzt_worlds_1997": [],
        "zzt_worlds_1998": [],
        "zzt_worlds_1999": [],
        "zzt_worlds_2000": [],
        "zzt_worlds_2001": [],
        "zzt_worlds_2002": [],
        "zzt_worlds_2003": [],
        "zzt_worlds_2004": [],
        "zzt_worlds_2005": [],
        "zzt_worlds_2006": [],
        "zzt_worlds_2007": [],
        "zzt_worlds_2008": [],
        "zzt_worlds_2009": [],
        "zzt_worlds_2010-2019": [],
        "zzt_worlds_2020-2029": [],
        "szzt_worlds": [],
        "utilities": [],
        "zig_worlds": [],
    }

    id_list = {
        "zzt_worlds_UNKNOWN": "",
        "zzt_worlds_1991": "",
        "zzt_worlds_1992": "",
        "zzt_worlds_1993": "",
        "zzt_worlds_1994": "",
        "zzt_worlds_1995": "",
        "zzt_worlds_1996": "",
        "zzt_worlds_1997": "",
        "zzt_worlds_1998": "",
        "zzt_worlds_1999": "",
        "zzt_worlds_2000": "",
        "zzt_worlds_2001": "",
        "zzt_worlds_2002": "",
        "zzt_worlds_2003": "",
        "zzt_worlds_2004": "",
        "zzt_worlds_2005": "",
        "zzt_worlds_2006": "",
        "zzt_worlds_2007": "",
        "zzt_worlds_2008": "",
        "zzt_worlds_2009": "",
        "zzt_worlds_2010-2019": "",
        "zzt_worlds_2020-2029": "",
        "szzt_worlds": "",
        "utilities": "",
        "zig_worlds": "",
    }

    new_info = {}

    readme_names = {
        "szzt_worlds": "Super ZZT Worlds",
        "utilities": "Utilities",
        "zig_worlds": "ZIG Worlds",
    }

    readme_bodies = {
        "szzt_worlds": SZZT_HEADER,
        "utilities": UTIL_HEADER,
        "zig_worlds": ZIG_HEADER
    }

    special_zips = ("szzt_worlds", "utilities", "zig_worlds")

    # Get all files by release date
    qs = File.objects.all().order_by("release_date", "letter", "title")

    for f in qs:
        if f.is_zzt():
            if f.release_date is None:
                year = "UNKNOWN"
            elif f.release_date.year >= 2020:
                year = "2020-2029"
            elif f.release_date.year >= 2010:
                year = "2010-2019"
            else:
                year = str(f.release_date.year)

            # Add file to the ZZT year list
            file_list["zzt_worlds_" + year].append(f)
            id_list["zzt_worlds_" + year] += str(f.id)
        if f.is_super_zzt():
            file_list["szzt_worlds"].append(f)
            id_list["szzt_worlds"] += str(f.id)
        if f.is_utility():
            file_list["utilities"].append(f)
            id_list["utilities"] += str(f.id)
        if f.is_zig():
            file_list["zig_worlds"].append(f)
            id_list["zig_worlds"] += str(f.id)

    # Set up names for zip files
    zip_names = file_list.keys()

    # Populate the zips
    for zip_name in zip_names:
        file_listing = ""
        zf = zipfile.ZipFile(
            os.path.join(CRON_ROOT, zip_name + ".zip"), "w"
        )

        # Add the relevant files
        for f in file_list[zip_name]:
            try:
                zf.write(f.phys_path(), arcname=os.path.basename(f.phys_path()))
                f_rd = str(f.release_date) if f.release_date is not None else ""
                file_listing += '{} "{}" by {} [{}]'.format(f_rd, f.title, f.author, f.filename).strip() + "\n"
                pass
            except FileNotFoundError:
                print('File not found: "{}"'.format(f.phys_path()))
                continue

        # Format the readme
        category = readme_names.get(zip_name, zip_name.split("_")[-1])
        readme_name = "Museum of ZZT Collection - {}.txt".format(category)
        readme_body = readme_bodies.get(zip_name, HEADER)
        if zip_name not in special_zips:
            readme_body = readme_body.format(zip_name.split("_")[-1], len(file_list[zip_name]))
        else:
            readme_body = readme_body.format(len(file_list[zip_name]))

        # Add file listing and footer
        readme_body += file_listing
        readme_body += FOOTER
        zf.writestr(readme_name, readme_body)

        # Calculate md5 checksum (zips will have new md5s every time so it has to be something else)
        md5 = hashlib.md5()
        md5.update(id_list[zip_name].encode("utf-8"))
        md5 = md5.hexdigest()

        # Update the JSON info
        new_info[zip_name] = {
            "group": zip_name,
            "md5": md5,
            "file_count": len(file_list[zip_name]),
            "date": str(datetime.now())
        }

    # Check for different checksums against existing JSON data
    to_replace = [] # Groups of files to actually update
    with open(os.path.join(SITE_ROOT, "museum_site", "static", "data", "mass_dl.json"), "r") as fh:
        raw = fh.read()
        data = json.loads(raw)

    for zip_name in zip_names:
        info = data.get(zip_name)
        if not info:
            info = {
                "group": zip_name,
                "md5": "",
                "file_count": 0,
                "date": "1970-01-01"
            }

        # Compare data and replace the zip if needed
        if (new_info[zip_name]["md5"] != info["md5"]) or (new_info[zip_name]["file_count"] != info["file_count"]):
            print(zip_name, "HAS CHANGED")

            # Replace any zips that need to be replaced
            try:
                src = os.path.join(SITE_ROOT, "tools", "crons", "{}.zip".format(zip_name))
                dst = os.path.join(SITE_ROOT, "zgames", "mass", "{}.zip".format(zip_name))
                shutil.move(src, dst)
            except:
                print("Failed to move", src)

        # Remove the zip
        try:
            os.remove(os.path.join(SITE_ROOT, "tools", "crons", "{}.zip".format(zip_name)))
        except:
            continue

    # Save the new information
    with open(os.path.join(SITE_ROOT, "museum_site", "static", "data", "mass_dl.json"), "w") as fh:
        fh.write(json.dumps(new_info))

    return True

if __name__ == "__main__":
    main()
