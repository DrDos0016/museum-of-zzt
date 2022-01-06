import os
import sys

from datetime import datetime, timedelta, timezone

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402
from museum_site.common import *  # noqa: E402
from museum_site.constants import *  # noqa: E402


def main():
    if len(sys.argv) == 2:
        year = sys.argv[-1]
    else:
        year = "2021"
    start_date = year + "-01-01 00:00:00Z"
    end_date = year + "-12-31 23:59:59Z"
    # Total uploads
    total = 0
    qs = Upload.objects.filter(date__gte=start_date, date__lte=end_date).exclude(file_id=None)
    total = len(qs)
    print("TOTAL UPLOADS", total)

    print("-" * 60)
    # Uploads by release date year
    years = {
        "None": 0,
        "1991": 0,
        "1992": 0,
        "1993": 0,
        "1994": 0,
        "1995": 0,
        "1996": 0,
        "1997": 0,
        "1998": 0,
        "1999": 0,
        "2000": 0,
        "2001": 0,
        "2002": 0,
        "2003": 0,
        "2004": 0,
        "2005": 0,
        "2006": 0,
        "2007": 0,
        "2008": 0,
        "2009": 0,
        "2010": 0,
        "2011": 0,
        "2012": 0,
        "2013": 0,
        "2014": 0,
        "2015": 0,
        "2016": 0,
        "2017": 0,
        "2018": 0,
        "2019": 0,
        "2020": 0,
        "2021": 0,
        "2022": 0,
    }
    for u in qs:
        year = str(u.file.release_date)[:4]
        years[year] = years[year] + 1
    for y in years.keys():
        print(y, years[y])

    print("-" * 60)
    # Uploads by platform
    names = {
        15:"ZZT",
        13:"Super ZZT",
        16:"ZIG",
        27:"Clone",
        33:"Program",
        35:"Rom",
    }
    lookups = [DETAIL_ZZT, DETAIL_SZZT, DETAIL_ZIG, DETAIL_CLONE_WORLD, DETAIL_PROGRAM, DETAIL_ROM]
    details = {
        DETAIL_ZZT: 0,
        DETAIL_SZZT: 0,
        DETAIL_ZIG: 0,
        DETAIL_CLONE_WORLD: 0,
        DETAIL_PROGRAM: 0,
        DETAIL_ROM: 0,
    }
    for u in qs:
        f_details = u.file.details.all().values_list("id", flat=True)
        for l in f_details:
            if l in lookups:
                details[l] = details[l] + 1

    print("Platform totals:")
    for d in details.keys():
        print(names[d], details[d])

    print("-" * 60)
    # Uploads by Author
    author_stats = {}
    author_stats_this_year = {}
    for u in qs:
        authors = u.file.author.split("/")
        for a in authors:
            author_stats[a] = author_stats.get(a, 0) + 1
            if u.file.release_date and str(u.file.release_date) >= start_date:
                author_stats_this_year[a] = author_stats_this_year.get(a, 0) + 1

    print("ALL UPLOADS ================================")
    for a in author_stats.keys():
        if author_stats[a] > 2:
            print(a + ";" + str(author_stats[a]))
    print(len(author_stats), "total authors")

    print("2021 RELEASES ===============================")
    for a in author_stats_this_year.keys():
        print(a + ";" + str(author_stats_this_year[a]))

    print("UPLOAD QUEUE BY DATE")

    print("DATE\tQUEUE")
    start_date = datetime(year=2020, month=6, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)
    for idx in range(0, 365):
        comp_date = datetime(year=2021, month=1, day=1, hour=11, minute=59, second=59, tzinfo=timezone.utc)
        delta = timedelta(days=idx)
        comp_date = comp_date + delta
        cd_str = str(comp_date)[:10]

        # Find Uploads from Start date through Compdate
        uploads = Upload.objects.filter(date__gte=start_date, date__lte=comp_date)

        # Of that set, count the ones that have a publish date in the future
        queue_size = 0
        for u in uploads:
            if not u.file:
                continue
            if u.file.publish_date > comp_date:
                queue_size += 1

        print(cd_str + "\t" + str(queue_size))



    return True


if __name__ == '__main__':
    main()
