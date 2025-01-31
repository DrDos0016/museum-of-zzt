import os
import sys

from datetime import datetime, timedelta, timezone

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402
from museum_site.constants import *  # noqa: E402
from museum_site.core.detail_identifiers import *  #noqa: E402

LAST_YEAR = "2024"
THIS_YEAR = "2025"
LAST_YEAR_START = "{}-01-01".format(LAST_YEAR)
LAST_YEAR_END = "{}-12-31".format(LAST_YEAR)
THIS_YEAR_START = "{}-01-01".format(THIS_YEAR)
THIS_YEAR_END = "{}-12-31".format(THIS_YEAR)

DETAIL_NAMES = names = {
    10:"Modified Graphics",
    15:"ZZT",
    13:"Super ZZT",
    16:"ZIG",
    21:"ZZT Board",
    27:"Clone",
    28:"Source Code",
    33:"Program",
    35:"Rom",
    37:"Weave ZZT",
    31:"Image",
    29:"Text",
    25:"ZZT High Score",
    39:"New Find",
    34:"Compressed",
    30:"HTML",
}

def main():
    if len(sys.argv) == 2:
        year = sys.argv[-1]
    else:
        year = LAST_YEAR  # The concluded year
    print("Year:", year)
    start_date = year + "-01-01 00:00:00Z"
    end_date = year + "-12-31 23:59:59Z"

    # MASTER QUERY
    # Anything with an upload date of the completed year
    upload_objs = Upload.objects.filter(date__gte=LAST_YEAR_START, date__lte=LAST_YEAR_END)
    print("Found {} upload objects for {}.".format(len(upload_objs), LAST_YEAR))
    print("(This matches pub pack manual counts in 2.0.2.3. for sure)")

    zfile_objs = File.objects.filter(upload__in=upload_objs).order_by("pk")
    print("Of those uploads, {} ZFiles are associated with them".format(len(zfile_objs)))
    print("-" * 60)

    """
    # Uncomment this block to find orphaned Upload objects
    for u in upload_objs:
        pk = u.pk
        print("Upload #", pk)
        zf = File.objects.get(upload__id=pk)
    """

    # Release Years
    years = {"Unknown": 0}
    for x in range(1991, int(LAST_YEAR) + 1):
        years[str(x)] = 0
    for zf in zfile_objs:  # Increment counts
        if zf.release_year():
            years[zf.release_year()] = years[zf.release_year()] + 1
        else:
            years["Unknown"] = years["Unknown"] + 1
    # Output
    print("YEAR;RELEASES")
    for k, v in years.items():
        print("{};{}".format(k,v))
    print("-" * 60)

    # Releases By Platform
    platform_counts = {DETAIL_ZZT: 0, DETAIL_SZZT: 0, DETAIL_WEAVE: 0, DETAIL_ROM: 0, DETAIL_CLONE_WORLD:0, DETAIL_ZIG: 0, DETAIL_PROGRAM: 0}
    for zf in zfile_objs:
        zf_details = list(zf.details.all().values_list(flat=True))
        for k in platform_counts.keys():
            if k in zf_details:
                platform_counts[k] += 1
    # Output
    print("PLATFORM;RELEASES")
    for k, v in platform_counts.items():
        print("{};{}".format(DETAIL_NAMES[k], v))
    print("-" * 60)

    # Releases By Author
    author_counts = {}
    for zf in zfile_objs:
        zf_authors = list(zf.authors.all().values_list("title", flat=True))
        for a in zf_authors:
            author_counts[a] = author_counts.get(a, 0) + 1
    # Output
    print("AUTHOR;RELEASES")
    for k, v in author_counts.items():
        if v < 2:  # Enforce minimum release count
            continue
        print("{};{}".format(k, v))
    print("-" * 60)

    print("UPLOAD QUEUE BY DATE")
    print("see log file.")
    print("-" * 60)

    # GA: Most Played Files
    # GA: Most Viewed Files

    print("AVG REVIEW SCORE BY YEAR lol=================================")
    qs = Review.objects.all().order_by("id")
    data = {}
    for r in qs:
        if r.rating == -1:
            continue

        if r.zfile:
            f = r.zfile
        else:
            continue

        if not f.release_date:
            continue

        year = f.release_date.year
        if not data.get(year):
            data[year] = {
                "total": 0,
                "reviews": 0
            }

        data[year]["total"] = data[year]["total"] + r.rating
        data[year]["reviews"] = data[year]["reviews"] + 1

    keys = data.keys()
    keys = sorted(keys)

    for k in keys:
        print(
            str(k) + ";" +
            str(round((data[k]["total"] / data[k]["reviews"]), 3))
        )
    return True

if __name__ == '__main__':
    main()
