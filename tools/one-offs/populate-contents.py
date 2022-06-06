import os
import sys
import zipfile

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402
from museum_site.common import zipinfo_datetime_tuple_to_str


def main():
    print("This tool will create Content objects for all File objects")
    input("Press Enter to continue.")

    qs = File.objects.all().order_by("id")

    for f in qs:
        if not f.file_exists():
            print("Skipping", f)
            continue
        print(f)

        try:
            zf = zipfile.ZipFile(f.phys_path())
        except zipfile.BadZipFile:
            print("Skipping ZF", f.phys_path())

        for zi in zf.infolist():
            zfile_id = f.id

            title = os.path.basename(zi.filename)
            path = zi.filename
            ext = os.path.splitext(zi.filename)[1]
            mod_date = zipinfo_datetime_tuple_to_str(zi)
            directory = zi.is_dir()
            crc32 = zi.CRC
            size = zi.file_size

            skip = False
            content = f.content.all()
            for c in content:
                if c.title == title and c.crc32 == crc32:
                    skip = True
                    break

            if skip:
                continue


            content = Content(
                title=title,
                path=path,
                ext=ext,
                mod_date=mod_date,
                directory=directory,
                crc32=crc32,
                size=size,
            )
            content.save()

            f.content.add(content)

    return True


if __name__ == '__main__':
    main()
