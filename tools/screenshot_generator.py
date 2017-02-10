import os
import sys
import zipfile

import django
import zookeeper

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import File


def main():
    print("Generate screenshots for: ")
    print("ALL - All Files")
    print("BLANK - Files with no screenshot set")
    print("<#> - File ID #")
    print("<[a-z]> - Letter")
    choice = input("Enter choice: ").upper()

    mode = "auto"
    if choice == "ALL":
        files = File.objects.all().order_by("letter", "title")
    elif choice == "BLANK":
        files = File.objects.filter(screenshot="").order_by("letter", "title")
    elif choice in (["1", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                    "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
                    "V", "W", "X", "Y", "Z"]):
        files = File.objects.filter(letter=(choice.lower()))
    else:
        files = File.objects.filter(pk=int(choice))
        mode = "manual"

    for f in files:
        print(f.letter, f.filename)
        try:
            zf = zipfile.ZipFile(
                "/var/projects/museum/zgames/" +
                f.letter + "/" + f.filename
            )
        except (FileNotFoundError, zipfile.BadZipFile):
            print("\tSkipping due to bad zip")
            continue

        file_list = zf.namelist()

        zzt_count = 0
        com_count = 0
        oldest_file = None
        oldest_date = "9999-12-31 23:59:59"
        for file in file_list:
            name, ext = os.path.splitext(file)
            ext = ext.upper()

            if ext == ".ZZT":  # ZZT File
                zzt_count += 1
                info = zf.getinfo(file)
                ymd = (str(info.date_time[0]) + "-" +
                       str(info.date_time[1]).zfill(2) + "-" +
                       str(info.date_time[2]).zfill(2) + " " +
                       str(info.date_time[3]).zfill(2) + ":" +
                       str(info.date_time[4]).zfill(2) + ":" +
                       str(info.date_time[5]).zfill(2))

                if ymd < oldest_date:
                    oldest_file = file
                    oldest_date = ymd

            if ext == ".COM":  # Com File means a font, and skip
                print("\tSkipping due to COM file")
                continue

        # Confirm there's a ZZT file
        if oldest_file is None:
            print("\tSkipping due to no ZZT file")
            continue

        # Extract the file
        """
        try:
            zf.extract(oldest_file, path="/var/projects/museum/tools/extract")
        except:
            print("\tSkipping due to bad zip to extract")
            continue
        """

        zf.extract(oldest_file, path="/var/projects/museum/tools/extract")

        # Render the screenshot
        z = zookeeper.Zookeeper(
            os.path.join("/var/projects/museum/tools/extract", oldest_file)
        )

        z.boards[0].screenshot(
            "/var/projects/museum/z2_site/static/images/screenshots/{}/{}".format(
                f.letter,
                f.filename[:-4]
            )
        )

        # Update the DB entry
        f.screenshot = f.filename[:-4] + ".png"
        f.save()
        print("SAVED ({})".format(f.screenshot))

    return True

if __name__ == "__main__":
    main()
