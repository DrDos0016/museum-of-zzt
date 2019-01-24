# This file doesn't care about "don't repeat yourself". Sorry.

import datetime
import hashlib
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

from museum_site.models import (File, DETAIL_ZZT, DETAIL_SZZT,
                                DETAIL_ZIG, DETAIL_UTILITY)

HEADER = """
T H E   M U S E U M   O F   Z Z T   P R E S E N T S

A compiliation of all ZZT worlds released in {} hosted on the Museum of ZZT.

To run:
- Download ZZT v3.2 from https://museumofzzt.com/file/z/zzt.zip
- Download DOSBox from http://www.dosbox.com
- Extract ZZT and any worlds you wish you play into a directory
- Mount the directory in DOSBox with the command:
  mount c C:\\path\\to\\ZZT\\directory
- Run ZZT.EXE and follow the on screen setup instructions
- Press W to bring up the world list and ENTER to select a world
- Press P to play!

For more detailed instructions, please refer to
https://museumofzzt.com/getting-started

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
    # Get ZZT worlds by release date
    zzt_worlds = File.objects.filter(
        details__id__in=[DETAIL_ZZT]
    ).order_by("release_date", "letter", "title")

    years = []
    mass_info = {}
    zf = None
    readme = ""
    file_count = 0
    ids = []
    readme_name = ""
    today = str(datetime.datetime.utcnow())[:10]

    for world in zzt_worlds:
        if world.release_date is None:
            year = "UNKNOWN"
        elif world.release_date.year >= 2010: # Group worlds from 2010-present
            year = "2010-" + today[:4]
        else:
            year = str(world.release_date.year)

        if year not in years:
            years.append(year)
            if zf is not None:
                with open("tmp-readme.txt", "w") as fh:
                    fh.write(HEADER.format(zip_year, file_count))
                    fh.write(readme)
                    fh.write(FOOTER)
                ret = zf.write("tmp-readme.txt", arcname=readme_name)
                zf.close()

                # Record info on the zip IDs
                ids = bytes(",".join(ids), "utf-8")
                md5 = hashlib.md5()
                md5.update(ids)
                md5 = md5.hexdigest()

                mass_info[zip_year] = {
                    "group": zip_year,
                    "md5": md5,
                    "file_count": file_count,
                    "date": today
                }


            zf = zipfile.ZipFile("/var/projects/museum/tools/crons/zzt_worlds_" + year + ".zip", "w")
            zip_year = year
            readme_name = "Museum of ZZT Collection - " + year + ".txt"
            file_count = 0
            ids = []
            readme = ""

        file_path = "/var/projects/museum/zgames/{}/{}".format(world.letter,
                                                               world.filename)

        zf.write(file_path, arcname=world.filename)
        if world.release_date is None:
            release = ""
        else:
            release = str(world.release_date)[:10]
        readme += (release + " " + world.title + " by " + world.author +
                   " [" + world.filename + "]").strip() + "\n"
        file_count += 1
        ids.append(str(world.id))

    # Finally, add the current year's manual and data
    zip_year = year
    readme_name = "Museum of ZZT Collection - " + zip_year + ".txt"

    with open("tmp-readme.txt", "w") as fh:
        fh.write(HEADER.format(zip_year, file_count))
        fh.write(readme)
        fh.write(FOOTER)
    ret = zf.write("tmp-readme.txt", arcname=readme_name)
    zf.close()

    # Record info on the zip ids
    ids = bytes(",".join(ids), "utf-8")
    md5 = hashlib.md5()
    md5.update(ids)
    md5 = md5.hexdigest()

    mass_info[zip_year] = {
        "group": zip_year,
        "md5": md5,
        "file_count": file_count,
        "date": today
    }

    # Get Super ZZT Worlds
    szzt_worlds = File.objects.filter(
        details__id__in=[DETAIL_SZZT]
    ).order_by("release_date", "letter", "title")

    years = []
    zf = zipfile.ZipFile("szzt_worlds.zip", "w")
    readme_name = "Museum of ZZT Collection - Super ZZT Worlds.txt"
    file_count = 0
    ids = []
    readme = ""

    for world in szzt_worlds:
        if world.release_date is None:
            year = "UNKNOWN"
        else:
            year = str(world.release_date.year)

        file_path = "/var/projects/museum/zgames/{}/{}".format(world.letter,
                                                               world.filename)
        zf.write(file_path, arcname=world.filename)
        if world.release_date is None:
            release = ""
        else:
            release = str(world.release_date)[:10]
        readme += (release + " " + world.title + " by " + world.author +
                   " [" + world.filename + "]").strip() + "\n"
        file_count += 1
        ids.append(str(world.id))

    with open("tmp-readme.txt", "w") as fh:
        fh.write(SZZT_HEADER.format(file_count))
        fh.write(readme)
        fh.write(FOOTER)
    zf.write("tmp-readme.txt", arcname=readme_name)
    zf.close()

    # Record info on the zip ids
    ids = bytes(",".join(ids), "utf-8")
    md5 = hashlib.md5()
    md5.update(ids)
    md5 = md5.hexdigest()

    mass_info["SZZT"] = {
        "group": "SZZT",
        "md5": md5,
        "file_count": file_count,
        "date": today
    }

    # Get ZIG Worlds
    zig_worlds = File.objects.filter(
        details__id__in=[DETAIL_ZIG]
    ).order_by("release_date", "letter", "title")

    years = []
    readme_name = ""
    zf = zipfile.ZipFile("zig_worlds.zip", "w")
    readme_name = "Museum of ZZT Collection - ZIG Worlds.txt"
    file_count = 0
    ids = []
    readme = ""

    for world in zig_worlds:
        if world.release_date is None:
            year = "UNKNOWN"
        else:
            year = str(world.release_date.year)

        file_path = "/var/projects/museum/zgames/{}/{}".format(world.letter,
                                                               world.filename)
        zf.write(file_path, arcname=world.filename)
        if world.release_date is None:
            release = ""
        else:
            release = str(world.release_date)[:10]
        readme += (release + " " + world.title + " by " + world.author +
                   " [" + world.filename + "]").strip() + "\n"
        file_count += 1
        ids.append(str(world.id))

    with open("tmp-readme.txt", "w") as fh:
        fh.write(ZIG_HEADER.format(file_count))
        fh.write(readme)
        fh.write(FOOTER)
    zf.write("tmp-readme.txt", arcname=readme_name)
    zf.close()

    # Record info on the zip ids
    ids = bytes(",".join(ids), "utf-8")
    md5 = hashlib.md5()
    md5.update(ids)
    md5 = md5.hexdigest()

    mass_info["ZIG"] = {
        "group": "ZIG",
        "md5": md5,
        "file_count": file_count,
        "date": today
    }

    # Get Utilities
    utilities = File.objects.filter(
        details__id__in=[DETAIL_UTILITY]
    ).order_by("release_date", "letter", "title")

    years = []
    readme_name = ""
    zf = zipfile.ZipFile("utilities.zip", "w")
    readme_name = "Museum of ZZT Collection - Utilities.txt"
    file_count = 0
    ids = []
    readme = ""

    for world in utilities:
        if world.release_date is None:
            year = "UNKNOWN"
        else:
            year = str(world.release_date.year)

        file_path = "/var/projects/museum/zgames/{}/{}".format(world.letter,
                                                               world.filename)
        zf.write(file_path, arcname=world.filename)
        if world.release_date is None:
            release = ""
        else:
            release = str(world.release_date)[:10]
        readme += (release + " " + world.title + " by " + world.author +
                   " [" + world.filename + "]").strip() + "\n"
        file_count += 1
        ids.append(str(world.id))

    with open("tmp-readme.txt", "w") as fh:
        fh.write(UTIL_HEADER.format(file_count))
        fh.write(readme)
        fh.write(FOOTER)
    zf.write("tmp-readme.txt", arcname=readme_name)
    zf.close()

    # Record info on the zip
    ids = bytes(",".join(ids), "utf-8")
    md5 = hashlib.md5()
    md5.update(ids)
    md5 = md5.hexdigest()

    mass_info["UTIL"] = {
        "group": "UTIL",
        "md5": md5,
        "file_count": file_count,
        "date": today
    }

    # Check for different checksums against existing JSON data
    to_replace = [] # Groups of files to actually update
    with open("/var/projects/museum/museum_site/static/data/mass_dl.json", "r") as fh:
        raw = fh.read()
        data = json.loads(raw)

    # DEBUG MD5
    """
    print("OLD / NEW")
    sorted_keys = list(mass_info.keys())
    sorted_keys.sort()
    for k in sorted_keys:
        print((k + "         ")[:10], data[k]["md5"], mass_info[k]["md5"], (data[k]["md5"] == mass_info[k]["md5"]))
    """

    # Replace any zips that need to be replaced
    try:
        src = "/var/projects/museum/tools/crons/zzt_worlds_UNKNOWN.zip"
        dst = "/var/projects/museum/zgames/mass/zzt_worlds_UNKNOWN.zip"
        shutil.move(src, dst)
    except:
        print("Failed to move", src)

    if data["UNKNOWN"]["md5"] == mass_info["UNKNOWN"]["md5"]:
        mass_info["UNKNOWN"] = data["UNKNOWN"]

    # Move Years
    for x in range(1991, 2010):
        try:
            src = "/var/projects/museum/tools/crons/zzt_worlds_" + str(x) + ".zip"
            dst = "/var/projects/museum/zgames/mass/zzt_worlds_" + str(x) + ".zip"
            shutil.move(src, dst)
        except:
            print("Failed to move", src)

        if data[str(x)]["md5"] == mass_info[str(x)]["md5"]:
            mass_info[str(x)] = data[str(x)]

    # Move 2010-Present
    try:
        src = "/var/projects/museum/tools/crons/zzt_worlds_2010-"+ today[:4] +".zip"
        dst = "/var/projects/museum/zgames/mass/zzt_worlds_2010-"+ today[:4] +".zip"
        shutil.move(src, dst)
    except:
        print("Failed to move", src)

    if data["2010-" + today[:4]]["md5"] == mass_info["2010-" + today[:4]]["md5"]:
        mass_info["2010-" + today[:4]] = data["2010-" + today[:4]]

    # Move Super ZZT
    try:
        src = "/var/projects/museum/tools/crons/szzt_worlds.zip"
        dst = "/var/projects/museum/zgames/mass/szzt_worlds.zip"
        shutil.move(src, dst)
    except:
        print("Failed to move", src)

    if data["SZZT"]["md5"] == mass_info["SZZT"]["md5"]:
        mass_info["SZZT"] = data["SZZT"]

    # Move ZIG (oh my god)
    try:
        src = "/var/projects/museum/tools/crons/zig_worlds.zip"
        dst = "/var/projects/museum/zgames/mass/zig_worlds.zip"
        shutil.move(src, dst)
    except:
        print("Failed to move", src)

    if data["ZIG"]["md5"] == mass_info["ZIG"]["md5"]:
        mass_info["ZIG"] = data["ZIG"]

    # Move Utilities
    try:
        src = "/var/projects/museum/tools/crons/utilities.zip"
        dst = "/var/projects/museum/zgames/mass/utilities.zip"
        shutil.move(src, dst)
    except:
        print("Failed to move", src)

    if data["UTIL"]["md5"] == mass_info["UTIL"]["md5"]:
        mass_info["UTIL"] = data["UTIL"]

    # Save JSON data
    with open("/var/projects/museum/museum_site/static/data/mass_dl.json", "w") as fh:
        fh.write(json.dumps(mass_info))

    return True

if __name__ == "__main__":
    main()
