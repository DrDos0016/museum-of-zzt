import os
import sys
import zipfile

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "z2.settings")
django.setup()

from z2_site.models import *


def main():
    input("Press enter to begin setting details")

    files = File.objects.all().order_by("letter", "title")
    #files = File.objects.filter(pk=1201).order_by("letter", "title")

    for f in files:
        details = []
        print(f.letter, f.filename)
        try:
            zf = zipfile.ZipFile(
                "/var/projects/museum/zgames/" +
                f.letter + "/" + f.filename
            )
        except (FileNotFoundError, zipfile.BadZipFile):
            #print("\tSkipping due to bad zip")
            f.details.add(Detail.objects.get(pk=DETAIL_LOST))
            continue

        file_list = zf.namelist()

        for file in file_list:
            name, ext = os.path.splitext(file)
            ext = ext.upper()

            if ext == ".ZZT":  # ZZT File
                if DETAIL_ZZT not in details:
                    details.append(DETAIL_ZZT)

            if ext == ".COM":  # Com File
                if DETAIL_GFX not in details:
                    details.append(DETAIL_GFX)

            if ext == ".ZZM":  # ZZM File
                if DETAIL_ZZM not in details:
                    details.append(DETAIL_ZZM)

            if ext == ".SZT":  # Super ZZT File
                if DETAIL_SZZT not in details:
                    details.append(DETAIL_SZZT)

            if ext == ".ZIG":  # ZIG File
                if DETAIL_ZIG not in details:
                    details.append(DETAIL_ZIG)


        # Update detials based on old category field
        if getattr(f, "category", None):
            if f.category == "Utility" and DETAIL_UTILITY not in details:
                details.append(DETAIL_UTILITY)

        # Update the DB entry
        if details:
            existing_qs = f.details.all().values_list("id", flat=True)
            existing = []
            for e in existing_qs:
                existing.append(e)
            #print("EXISTING", existing)
            for d in details:
                if d not in existing:  # Add new detail
                    f.details.add(Detail.objects.get(pk=d))
                    #f.save()

            #print(details)
            #f.screenshot = f.filename[:-4] + ".png"
            #f.save()
            #print("SAVED ({})".format(f.screenshot))

    return True

if __name__ == "__main__":
    main()
