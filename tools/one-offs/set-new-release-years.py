import os
import sys

from datetime import date

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

UPDATES = [
    #(PK, YEAR)
    (3691, 1995),
    (2895, 1996),
    (3526, 2002),
    (1648, 1995),
    (1362, 1994),
    (4037, 1998),
    (3244, 2000),
    (703, 1991),
    (2957, 2002),
    (1362, 1994),
    (3534, 1996),
    (3244, 2000),
    (703, 1991),
    (2957, 2002),
    (3294, 1997),
    (1100, 2000),
    (3701, 1996),
    (2949, 2018),
    (3441, 1994),
    (2550, 1995),
    (2551, 1997),
    (3262, 1993),
    (1394, 1997),
    (2991, 1996),
    (3184, 1997),
    (2528, 1992),
    (4030, 1995),
    (4053, 1999),
    (3577, 1995),
]


def main():
    print("This script will set the release year file on various ZFiles with unknown release dates")
    input("Press ENTER to begin.")

    for (pk, year) in UPDATES:
        zf = File.objects.filter(pk=pk).first()
        if not zf:
            print("ZFILE NOT FOUND", pk)
            continue
        zf.year = date(year=year, month=1, day=1)
        zf.save()
        print(zf, "release year set to", year)
    return True


if __name__ == '__main__':
    main()
