import os
import sys
import zipfile

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402
from museum_site.common import SITE_ROOT  # noqa: E402


Z_EXTRACT = os.path.join(SITE_ROOT, "tools", "z-extract")


def find_destination(f):
    if f.id < 1000:
        r = "0000-0999"
    elif f.id < 2000:
        r = "1000-1999"
    elif f.id < 3000:
        r = "2000-2999"
    elif f.id < 4000:
        r = "3000-3999"
    elif f.id < 5000:
        r = "4000-4999"
    elif f.id < 6000:
        r = "5000-5999"
    elif f.id < 7000:
        r = "6000-6999"
    elif f.id < 8000:
        r = "7000-7999"
    elif f.id < 9000:
        r = "8000-8999"
    else:
        r = "9000-9999"

    f_dir = ("0000" + str(f.id))[-4:] + "-" + f.filename[:-4]
    output = os.path.join(Z_EXTRACT, r, f_dir)
    return output


def main():
    if not os.path.isdir(Z_EXTRACT):
        os.mkdir(Z_EXTRACT)

    for d in [
        "0000-0999", "1000-1999", "2000-9999", "3000-3999", "4000-4999",
        "5000-5999", "6000-6999", "7000-7999", "8000-8999", "9000-9999",
    ]:
        if not os.path.isdir(os.path.join(Z_EXTRACT, d)):
            os.mkdir(os.path.join(Z_EXTRACT, d))

    qs = File.objects.filter(pk__gte=2800).order_by("id")

    for f in qs:
        if not f.file_exists():
            print("ERROR:", f.phys_path(), "does not exist")
            continue

        destination = find_destination(f)

        try:
            zf = zipfile.ZipFile(f.phys_path())
        except zipfile.BadZipFile as e:
            print("BAD ZIP ON", f)
            print(e)
            continue

        try:
            zf.extractall(path=destination)
        except OSError as e:
            print("ERROR ON", f)
            print(e)
        except NotImplementedError as e:
            print("BAD COMPRESSION ON", f)
            print(e)
    return True


if __name__ == '__main__':
    main()
