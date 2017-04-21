# This file doesn't care about "don't repeat yourself". Sorry.

import datetime
import json
import os
import shutil
import subprocess
import sys
import zipfile

import django

sys.path.append("/var/projects/museum")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import (File, DETAIL_ZZT, DETAIL_SZZT,
                            DETAIL_ZIG, DETAIL_UTILITY)

HEADER = """
T H E   M U S E U M   O F   Z Z T   P R E S E N T S

A compiliation of all ZZT worlds released in {} hosted on the Museum of ZZT.

To run:
- Download ZZT v3.2 from https://z2.pokyfriends.com/file/z/zzt.zip
- Download DOSBox from http://www.dosbox.com
- Extract ZZT and any worlds you wish you play into a directory
- Mount the directory in DOSBox with the command:
  mount c C:\\path\\to\\ZZT\\directory
- Run ZZT.EXE and follow the on screen setup instructions
- Press W to bring up the world list and ENTER to select a world
- Press P to play!

For more detailed instructions, please refer to
https://museumofzzt.com/getting-started

{} Files are included in this compilation:

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
    readme_name = ""
    today = str(datetime.datetime.utcnow())[:10]

    for world in zzt_worlds:
        if world.release_date is None:
            year = "UNKNOWN"
        else:
            year = str(world.release_date.year)

        if year not in years:
            years.append(year)
            if zf is not None:
                with open("tmp-readme.txt", "w") as fh:
                    fh.write(HEADER.format(zip_year, file_count))
                    fh.write(readme)
                    fh.write(FOOTER)
                zf.write("tmp-readme.txt", arcname=readme_name)
                zf.close()

                # Record info on the zip
                resp = subprocess.run(
                    ["md5sum", "zzt_worlds_" + zip_year + ".zip"],
                    stdout=subprocess.PIPE
                )
                md5 = resp.stdout[:32].decode("utf-8")

                mass_info[zip_year] = {
                    "group": zip_year,
                    "md5": md5,
                    "file_count": file_count,
                    "date": today
                }


            zf = zipfile.ZipFile("zzt_worlds_" + year + ".zip", "w")
            zip_year = year
            readme_name = "Museum of ZZT Collection - " + year + ".txt"
            file_count = 0
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

    # Get Super ZZT Worlds
    szzt_worlds = File.objects.filter(
        details__id__in=[DETAIL_SZZT]
    ).order_by("release_date", "letter", "title")

    years = []
    zf = None
    readme = ""
    file_count = 0
    readme_name = ""

    zf = zipfile.ZipFile("szzt_worlds.zip", "w")
    readme_name = "Museum of ZZT Collection - Super ZZT Worlds.txt"
    file_count = 0
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

    with open("tmp-readme.txt", "w") as fh:
        fh.write(HEADER.format(zip_year, file_count))
        fh.write(readme)
        fh.write(FOOTER)
    zf.write("tmp-readme.txt", arcname=readme_name)
    zf.close()

    # Record info on the zip
    resp = subprocess.run(["md5sum", "szzt_worlds.zip"],
                          stdout=subprocess.PIPE)
    md5 = resp.stdout[:32].decode("utf-8")

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
    zf = None
    readme = ""
    file_count = 0
    readme_name = ""

    zf = zipfile.ZipFile("zig_worlds.zip", "w")
    readme_name = "Museum of ZZT Collection - ZIG Worlds.txt"
    file_count = 0
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

    with open("tmp-readme.txt", "w") as fh:
        fh.write(HEADER.format(zip_year, file_count))
        fh.write(readme)
        fh.write(FOOTER)
    zf.write("tmp-readme.txt", arcname=readme_name)
    zf.close()

    # Record info on the zip
    resp = subprocess.run(["md5sum", "zig_worlds.zip"],
                          stdout=subprocess.PIPE)
    md5 = resp.stdout[:32].decode("utf-8")

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
    zf = None
    readme = ""
    file_count = 0
    readme_name = ""

    zf = zipfile.ZipFile("utilities.zip", "w")
    readme_name = "Museum of ZZT Collection - Utilities.txt"
    file_count = 0
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

    with open("tmp-readme.txt", "w") as fh:
        fh.write(HEADER.format(zip_year, file_count))
        fh.write(readme)
        fh.write(FOOTER)
    zf.write("tmp-readme.txt", arcname=readme_name)
    zf.close()

    # Record info on the zip
    resp = subprocess.run(["md5sum", "utilities.zip"],
                          stdout=subprocess.PIPE)
    md5 = resp.stdout[:32].decode("utf-8")

    mass_info["UTIL"] = {
        "group": "UTIL",
        "md5": md5,
        "file_count": file_count,
        "date": today
    }

    # Check for different checksums against existing JSON data

    # Replace any zips that need to be replaced
    src = "/var/projects/museum/tools/crons/zzt_worlds_UNKNOWN.zip"
    dst = "/var/projects/museum/zgames/mass/zzt_worlds_UNKNOWN.zip"
    shutil.move(src, dst)

    for x in range(1990, 2017):
        try:
            src = "/var/projects/museum/tools/crons/zzt_worlds_" + str(x) + ".zip"
            dst = "/var/projects/museum/zgames/mass/zzt_worlds_" + str(x) + ".zip"
            shutil.move(src, dst)
        except:
            None

    try:
        src = "/var/projects/museum/tools/crons/szzt_worlds.zip"
        dst = "/var/projects/museum/zgames/mass/szzt_worlds.zip"
        shutil.move(src, dst)
    except:
        None

    try:
        src = "/var/projects/museum/tools/crons/zig_worlds.zip"
        dst = "/var/projects/museum/zgames/mass/zig_worlds.zip"
        shutil.move(src, dst)
    except:
        None

    try:
        src = "/var/projects/museum/tools/crons/utilities.zip"
        dst = "/var/projects/museum/zgames/mass/utilities.zip"
        shutil.move(src, dst)
    except:
        None

    # Save JSON data
    with open("/var/projects/museum/z2_site/static/data/mass_dl.json", "w") as fh:
        fh.write(json.dumps(mass_info))

    return True

if __name__ == "__main__":
    main()
