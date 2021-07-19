import os
import sys
import zipfile

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402
from museum_site.constants import *  # noqa: E402


def main():
    print(
        "This script will analyze the file extensions used in every zip and "
        "determine what details should likely be associated with them."
    )
    print("Starting...")
    unknown_extensions = {}
    qs = File.objects.all().order_by("id")
    print("Iterating...")

    for zgame in qs:
        if os.path.isfile(zgame.phys_path()) and zgame.filename.lower().endswith(".zip"):
            # Examine the zip
            zf = zipfile.ZipFile(zgame.phys_path())
            files = zf.namelist()
            for f in files:
                name = f.lower()
                #print(" - " + name)
                ext = os.path.splitext(os.path.basename(f).upper())
                if ext[1] == "":
                    ext = ext[0]
                else:
                    ext = ext[1]

                if ext in EXTENSION_HINTS:
                    continue
                elif ext == "":  # Folders hit this
                    continue
                elif ext in unknown_extensions:
                    unknown_extensions[ext].append(name + " - " + str(zgame))
                else:
                    unknown_extensions[ext] = [name + " - " + str(zgame)]

    for ue in unknown_extensions:
        print("=" * 40)
        print(ue)
        print("\n".join(unknown_extensions[ue]))
    print("Found", len(unknown_extensions), "unknown extensions")

    return True


if __name__ == '__main__':
    main()
