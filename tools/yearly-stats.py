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

LAST_YEAR = "2023"
THIS_YEAR = "2024"
LAST_YEAR_START = "{}-01-01".format(LAST_YEAR)
LAST_YEAR_END = "{}-12-31".format(LAST_YEAR)
THIS_YEAR_START = "{}-01-01".format(THIS_YEAR)
THIS_YEAR_END = "{}-12-31".format(THIS_YEAR)

def main():
    if len(sys.argv) == 2:
        year = sys.argv[-1]
    else:
        year = LAST_YEAR  # The concluded year
    print("Year:", year)
    start_date = year + "-01-01 00:00:00Z"
    end_date = year + "-12-31 23:59:59Z"
    # Total uploads
    total = 0
    qs = Upload.objects.filter(date__gte=start_date, date__lte=end_date)
    total = len(qs)
    print("TOTAL UPLOADS", total)

    print("-" * 60)
    # Uploads by release date year
    years = {"None": 0}
    for x in range(1991, int(LAST_YEAR) + 1):
        years[str(x)] = 0

    for u in qs:
        zf = File.objects.filter(upload__id=u.pk).first()
        if not zf:
            continue

        year = str(zf.release_date)[:4]
        years[year] = years[year] + 1
    for y in years.keys():
        print(y, years[y])

    print("-" * 60)
    # Uploads by platform
    names = {
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
    details = {}
    for u in qs:
        added_pk = False
        zf = File.objects.filter(upload__id=u.pk).first()
        if not zf:
            continue
        #print(zf)
        f_details = zf.details.all().values_list("id", flat=True)
        if not f_details:
            print("NO DETAILS?", zf)
        for l in f_details:
            if details.get(l) is not None:
                details[l] = details[l] + 1
            else:
                details[l] = 1

    print("Scanned", len(qs), "files")
    print("Platform totals:")
    for d in details.keys():
        print(names[d], details[d])

    print("-" * 60)


    # Uploads by Author
    author_stats = {}  # Any author that had something uploaded in <finished_year>
    author_stats_this_year = {}  # Any author that had something with a release year of <finished_year>
    for u in qs:  # All uploads for the year
        zf = File.objects.filter(upload=u).first()
        if not zf:
            continue
        authors = zf.authors.all()
        for a in authors:
            author_stats[a] = author_stats.get(a, 0) + 1
            if zf.release_date and str(zf.release_date) >= start_date:
                author_stats_this_year[a] = author_stats_this_year.get(a, 0) + 1

    qs = File.objects.filter(publish_date__gte=LAST_YEAR_START, publish_date__lte=THIS_YEAR_START)
    authors = {}
    for zf in qs:
        for author in zf.authors.all():
            if authors.get(author.title):
                authors[author.title] += 1
            else:
                authors[author.title] = 1

    """
    print(author_stats)
    print("="*80)
    print(author_stats_this_year)
    print("="*80)
    print(authors)
    """
    for k, v in author_stats.items():
        print(v, k.title.replace(" ", "_"))
    for k, v in authors.items():
        print(v, k.replace(" ", "_"))



    print("ALL UPLOADS ================================")
    for a in author_stats.keys():
        if author_stats[a] > 2:
            print(a)
            print(a + ";" + str(author_stats[a]))
    print(len(author_stats), "total authors")

    print("<YEAR> RELEASES ===============================")
    for a in author_stats_this_year.keys():
        print(a + ";" + str(author_stats_this_year[a]))

    print("UPLOAD QUEUE BY DATE")

    print("DATE\tQUEUE")
    print("--commented out since this is very poorly optimized and takes a few mins")
    """
    s_date = datetime(year=2020, month=6, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)
    for idx in range(0, 365):
        comp_date = datetime(year=2021, month=1, day=1, hour=11, minute=59, second=59, tzinfo=timezone.utc)
        delta = timedelta(days=idx)
        comp_date = comp_date + delta
        cd_str = str(comp_date)[:10]

        # Find Uploads from Start date through Compdate
        uploads = Upload.objects.filter(date__gte=s_date, date__lte=comp_date)

        # Of that set, count the ones that have a publish date in the future
        queue_size = 0
        for u in uploads:
            if not u.file:
                continue
            if u.file.publish_date > comp_date:
                queue_size += 1

        print(cd_str + "\t" + str(queue_size))
    """

    print("AVG REVIEW SCORE BY YEAR lol")
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
            str(k) + "\t" +
            str(round((data[k]["total"] / data[k]["reviews"]), 3))
        )


    return True


if __name__ == '__main__':
    main()
