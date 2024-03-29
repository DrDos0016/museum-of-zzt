# This file doesn't care about "don't repeat yourself". Sorry.

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

import django

from datetime import datetime

django.setup()

from museum_site.models import File  # noqa: E402

from museum_site.core.detail_identifiers import *
from museum_site.constants import SITE_ROOT, DATA_PATH  # noqa: E402

CRON_ROOT = os.path.join(SITE_ROOT, "tools", "crons")
MASS_DL_DATA_PATH = os.path.join(DATA_PATH, "mass_dl.json")
PREFIX = "moz-"
TEMP_DIR = tempfile.TemporaryDirectory(prefix=PREFIX)
TEMP_DIR_PATH = TEMP_DIR.name

HEADER = """
T H E   M U S E U M   O F   Z Z T   P R E S E N T S

A compiliation of all ZZT worlds released in {} hosted on the Museum of ZZT.

To run:
- Download ZZT v3.2 from https://museumofzzt.com/file/view/zzt/
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
- Download Super ZZT from https://museumofzzt.com/file/view/szzt/
- Extract Super ZZT and any worlds you wish you play into a directory
- Download the latest version of Zeta from https://zeta.asie.pl
- Extract Zeta into the directory containing Super ZZT and your Super
  ZZT worlds
- Run zeta86.exe and configure Super ZZT (You'll likely want "K"eyboard
  and "C"olor)
- Press W to bring up the world list and ENTER to select a world
- Press P to play!
- By default, Super ZZT's editor is restricted. To enable it, you must
  pass a commandline arugment to the program when launching zeta:
  `zeta86.exe -e "SUPERZ.EXE /e`

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

ZZM_HEADER = """
T H E   M U S E U M   O F   Z Z T   P R E S E N T S

A compiliation of all ZZT Audio Files hosted on the Museum of ZZT.

{} files are included in this compilation:

"""[1:]

FEATURED_HEADER = """
T H E   M U S E U M   O F   Z Z T   P R E S E N T S

A compiliation of all Featured Worlds hosted on the Museum of ZZT.

{} files are included in this compilation:

"""[1:]

WEAVE_HEADER = """
T H E   M U S E U M   O F   Z Z T   P R E S E N T S

A compiliation of all Weave ZZT worlds hosted on the Museum of ZZT.

{} files are included in this compilation:

"""[1:]

FOOTER = """
- https://museumofzzt.com -
"""

TEMPLATE_JSON = {
    "zzt_worlds_unknown": {"md5": "", "file_count": 0},
    "zzt_worlds_1991": {"md5": "", "file_count": 0},
    "zzt_worlds_1992": {"md5": "", "file_count": 0},
    "zzt_worlds_1993": {"md5": "", "file_count": 0},
    "zzt_worlds_1994": {"md5": "", "file_count": 0},
    "zzt_worlds_1995": {"md5": "", "file_count": 0},
    "zzt_worlds_1996": {"md5": "", "file_count": 0},
    "zzt_worlds_1997": {"md5": "", "file_count": 0},
    "zzt_worlds_1998": {"md5": "", "file_count": 0},
    "zzt_worlds_1999": {"md5": "", "file_count": 0},
    "zzt_worlds_2000": {"md5": "", "file_count": 0},
    "zzt_worlds_2001": {"md5": "", "file_count": 0},
    "zzt_worlds_2002": {"md5": "", "file_count": 0},
    "zzt_worlds_2003": {"md5": "", "file_count": 0},
    "zzt_worlds_2004": {"md5": "", "file_count": 0},
    "zzt_worlds_2005": {"md5": "", "file_count": 0},
    "zzt_worlds_2006": {"md5": "", "file_count": 0},
    "zzt_worlds_2007": {"md5": "", "file_count": 0},
    "zzt_worlds_2008": {"md5": "", "file_count": 0},
    "zzt_worlds_2009": {"md5": "", "file_count": 0},
    "zzt_worlds_2010-2019": {"md5": "", "file_count": 0},
    "zzt_worlds_2020-2029": {"md5": "", "file_count": 0},
    "szzt_worlds": {"md5": "", "file_count": 0},
    "utilities": {"md5": "", "file_count": 0},
    "zig_worlds": {"md5": "", "file_count": 0},
    "zzm_audio": {"md5": "", "file_count": 0},
    "featured_worlds": {"md5": "", "file_count": 0},
    "weave_worlds": {"md5": "", "file_count": 0},
}


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
        "zzm_audio": [],
        "featured_worlds": [],
        "weave_worlds": [],
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
        "zzm_audio": "",
        "featured_worlds": "",
        "weave_worlds": "",
    }

    new_info = {}

    readme_names = {
        "szzt_worlds": "Super ZZT Worlds",
        "utilities": "Utilities",
        "zig_worlds": "ZIG Worlds",
        "zzm_audio": "ZZM Audio Files",
        "featured_worlds": "Featured Worlds",
        "weave_worlds": "Weave ZZT Worlds",
    }

    readme_bodies = {
        "szzt_worlds": SZZT_HEADER,
        "utilities": UTIL_HEADER,
        "zig_worlds": ZIG_HEADER,
        "zzm_audio": ZZM_HEADER,
        "featured_worlds": FEATURED_HEADER,
        "weave_worlds": WEAVE_HEADER
    }

    special_zips = ("szzt_worlds", "utilities", "zig_worlds", "zzm_audio", "featured_worlds", "weave_worlds")

    # Get all files by release date
    qs = File.objects.all().order_by("release_date", "letter", "title")

    print("Iterating over files...")
    for f in qs:
        if f.is_detail(DETAIL_ZZT):
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
        if f.is_detail(DETAIL_SZZT):
            file_list["szzt_worlds"].append(f)
            id_list["szzt_worlds"] += str(f.id)
        if f.is_detail(DETAIL_UTILITY):
            file_list["utilities"].append(f)
            id_list["utilities"] += str(f.id)
        if f.is_detail(DETAIL_ZIG):
            file_list["zig_worlds"].append(f)
            id_list["zig_worlds"] += str(f.id)
        if f.is_detail(DETAIL_ZZM):
            file_list["zzm_audio"].append(f)
            id_list["zzm_audio"] += str(f.id)
        if f.is_detail(DETAIL_FEATURED):
            file_list["featured_worlds"].append(f)
            id_list["featured_worlds"] += str(f.id)
        if f.is_detail(DETAIL_WEAVE):
            file_list["weave_worlds"].append(f)
            id_list["weave_worlds"] += str(f.id)

    print("Files iterated.")

    # Set up names for zip files
    zip_names = file_list.keys()

    # Populate the zips
    for zip_name in zip_names:
        print("Creating", zip_name)
        file_listing = ""
        zf = zipfile.ZipFile(os.path.join(TEMP_DIR_PATH, zip_name + ".zip"), "w")

        # Add the relevant files
        for f in file_list[zip_name]:
            try:
                zf.write(f.phys_path(), arcname=os.path.basename(f.phys_path()))
                f_rd = str(f.release_date) if f.release_date is not None else ""
                file_listing += '{} "{}" by {} [{}]'.format(f_rd, f.title, ", ".join(f.related_list("authors")), f.filename).strip() + "\n"
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

        # Calculate md5 checksum (zips will have new md5s every time)
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
    to_replace = []  # Groups of files to actually update
    try:
        with open(MASS_DL_DATA_PATH, "r") as fh:
            raw = fh.read()
            data = json.loads(raw)
    except FileNotFoundError:
        data = TEMPLATE_JSON

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
        if (
            (new_info[zip_name]["md5"] != info["md5"]) or
            (new_info[zip_name]["file_count"] != info["file_count"]) or
            ("force" in sys.argv)
        ):
            print(zip_name, "HAS CHANGED")

            # Replace any zips that need to be replaced
            try:
                src = os.path.join(TEMP_DIR_PATH, "{}.zip".format(zip_name))
                dst = os.path.join(SITE_ROOT, "zgames", "mass", "{}.zip".format(zip_name))
                shutil.move(src, dst)
            except Exception:
                print("Failed to move", src)

        # Remove the zip
        try:
            os.remove(os.path.join(TEMP_DIR_PATH, "{}.zip".format(zip_name)))
        except Exception:
            continue

    # Save the new information
    with open(MASS_DL_DATA_PATH, "w") as fh:
        fh.write(json.dumps(new_info))

    print("Zips created.")
    return True


if __name__ == "__main__":
    main()
