import os
import sys
import zipfile

import django

import zookeeper

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import File  # noqa: E402
from museum_site.common import SITE_ROOT, TEMP_PATH


def main():
    pk = int(input("File ID: "))
    f = File.objects.get(pk=pk)
    print("Selected:", f)

    zf = zipfile.ZipFile(f.phys_path())
    file_list = zf.namelist()

    to_rip = []
    for fname in file_list:

        if fname.upper().endswith(".COM"):
            to_rip.append(fname)

    print("Found {} font(s)".format(len(to_rip)))

    if to_rip:
        for font_file in to_rip:
            padded_id = ("0000" + str(f.id))[-4:]
            museum_name = padded_id + "-" + font_file[:-4] + ".png"
            museum_path = os.path.join(SITE_ROOT, "museum_site", "static", "images", "charsets", museum_name)

            print("Ripping", font_file, "as", museum_name)
            zf.extract(font_file, path=TEMP_PATH)

            z = zookeeper.Zookeeper()
            z.export_font(os.path.join(TEMP_PATH, font_file), museum_path)
            print("Wrote", museum_path)
            print("Removing", font_file)
            os.remove(os.path.join(TEMP_PATH, font_file))
    print("Done.")

if __name__ == '__main__':
    main()
