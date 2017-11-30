import os
import sys
import zipfile

import django
import zookeeper

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File


def main():
    mode = "AUTO"

    while True:
        print("MODE:", mode)
        print("Enter AUTO or MANUAL to set mode")
        print("Generate screenshots for: ")
        print("ALL - All Files")
        print("BLANK - Files with no screenshot set")
        print("UPLOADED - Files that haven't been published")
        print("<#> - File ID #")
        print("<[a-z]> - Letter")
        print("TEMP - Whatever set I coded for this")
        choice = input("Enter choice: ").upper()

        if choice == "ALL":
            files = File.objects.all().order_by("letter", "title")
        elif choice == "UPLOADED":
            files = File.objects.filter(details__id__in=[18]) # UPLOADED
        elif choice == "BLANK":
            files = File.objects.filter(screenshot="").order_by("letter",
                                                                "title")
        elif choice in (["1", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                         "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
                         "V", "W", "X", "Y", "Z"]):
            files = File.objects.filter(letter=(choice.lower()))
        elif choice == "TEMP":
            ids = [
                42, 85, 97, 145, 2172, 593, 191, 188, 2116, 303, 314,
                352, 365, 382, 1282, 392, 459, 2186, 525, 533, 601, 626, 1245,
                674, 133, 966, 688, 689, 776, 758, 799, 848, 859, 1861, 1880,
                878, 906, 950, 999, 1690, 1127, 1057, 1051, 1137, 1033, 1034,
                1115, 1142, 1124, 3, 709, 1189, 1190, 2146, 1227, 17, 1263,
                801, 1284, 1285, 1760, 1315, 1853, 1361, 1360, 1627, 1380,
                1387, 1703, 625
            ]
            files = File.objects.filter(id__in=ids)
        elif choice == "AUTO" or choice == "MANUAL":
            mode = choice
            continue
        else:
            files = File.objects.filter(pk=int(choice))
        break

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
        zzt_list = []
        com_count = 0
        com_list = []
        oldest_file = None
        oldest_date = "9999-12-31 23:59:59"
        for file in file_list:
            name, ext = os.path.splitext(file)
            ext = ext.upper()

            if ext == ".ZZT":  # ZZT File
                zzt_count += 1
                zzt_list.append(file)
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
                com_count += 1
                com_list.append(file)
                continue

        # Confirm there's a ZZT file
        if oldest_file is None:
            print("\tSkipping due to no ZZT file")
            continue

        # Extract the file
        try:
            zf.extract(oldest_file, path="/var/projects/museum/tools/extract")
        except:
            print("\tSkipping due to bad zip to extract")
            continue

        if mode == "AUTO":
            zf.extract(oldest_file, path="/var/projects/museum/tools/extract")

            # Render the screenshot
            z = zookeeper.Zookeeper(
                os.path.join("/var/projects/museum/tools/extract", oldest_file)
            )

            z.boards[0].screenshot(
                ("/var/projects/museum/museum_site/static/images"
                 "/screenshots/{}/{}").format(
                    f.letter,
                    f.filename[:-4]
                ),
                title_screen=True
            )
        elif mode == "MANUAL":
            use_com = ""
            if com_list:
                if len(com_list) == 1:
                    use_com = com_list[0]
                else:
                    print(com_list)
                    use_com = com_list[int(input("IDX of com file to use: "))]
                zf.extract(use_com, path="/var/projects/museum/tools/extract")

            use_zzt = ""
            print(zzt_list)
            if len(zzt_list) == 1:
                use_zzt = zzt_list[0]
            else:
                print("Oldest:", oldest_file)
                use_zzt = zzt_list[int(input("IDX of ZZT file to use: "))]
            zf.extract(use_zzt, path="/var/projects/museum/tools/extract")



            if use_com:
                # Rip the charset
                z = zookeeper.Zookeeper()
                ret = z.export_font(
                    "/var/projects/museum/tools/extract/" + use_com,
                    "extract/temp.png"
                )

                charset = "/var/projects/museum/tools/extract/temp.png"

                z = zookeeper.Zookeeper(
                    os.path.join("/var/projects/museum/tools/extract", use_zzt),
                    charset
                )
            else:
                # Parse the file
                z = zookeeper.Zookeeper(
                    os.path.join("/var/projects/museum/tools/extract", use_zzt)
                )

            board_idx = int(input("Enter board IDX to render: "))
            z.boards[board_idx].screenshot(
                ("/var/projects/museum/museum_site/static/images"
                 "/screenshots/{}/{}", title).format(
                    f.letter,
                    f.filename[:-4]
                ),
                title_screen=True
            )

        # Update the DB entry
        f.screenshot = f.filename[:-4] + ".png"
        f.save()
        print("SAVED ({})".format(f.screenshot))

    return True

if __name__ == "__main__":
    main()
