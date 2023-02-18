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

now = datetime.utcnow()
year = now.year
jan_one = str(year) + "-01-01"
jan_one_dt = str(year) + "-01-01 00:00:00Z"

def main():
    stats = []
    today = str(now)[:10]
    stats.append("today={}".format(today))


    stats.append(calculate_queue_size())
    stats.append(calculate_total_files())
    stats.append(calculate_historic_files())
    stats.append(calculate_modern_files())
    stats.append(calculate_this_year_historic_files())
    stats.append(calculate_authors())
    stats.append(calculate_companies())
    stats.append(calculate_total_articles())

    """
    for raw in stats:
        (name, val) = raw.split("=")
        print(name, val)
    """

    stats_str = "|".join(stats)
    log_path = os.path.join(
        SITE_ROOT, "museum_site", "static", "data", "{}-stats.log".format(year)
    )
    with open(log_path, "a") as fh:
        fh.write(stats_str + "\n")

    return True

def calculate_queue_size():
    """ Count of unpublished files """
    output = File.objects.unpublished().count()
    return "queue_size={}".format(output)

def calculate_total_files():
    """ Raw count of File objects, including lost or anything else """
    output = File.objects.count()
    return "total_files={}".format(output)

def calculate_historic_files():
    """ Total Files from before the current year """
    output = File.objects.filter(release_date__lt=jan_one).count()
    unk = File.objects.filter(release_date=None).count()
    return "historic_files={}".format(output + unk)

def calculate_modern_files():
    """ Total Files from the current year """
    output = File.objects.filter(release_date__gte=jan_one).count()
    return "modern_files={}".format(output)

def calculate_this_year_historic_files():
    """ Historic Files uploaded this year """
    output = Upload.objects.filter(
        date__gte=jan_one_dt, file__release_date__lt=jan_one
    ).count()
    return "this_year_historic_files={}".format(output)

def calculate_authors():
    """ Total Authors """
    raw = File.objects.all()
    authors = []
    for ssv in raw:
        for a in ssv.get_related_list("authors", "title"):
            if a not in authors:
                authors.append(a)
    output = len(authors)
    return "authors={}".format(output)

def calculate_companies():
    """ Total Authors """
    raw = File.objects.all()
    authors = []
    for ssv in raw:
        for a in ssv.get_related_list("companies", "title"):
            if a not in authors:
                authors.append(a)
    output = len(authors)
    return "companies={}".format(output)

def calculate_total_articles():
    """ Total Articles """
    output = Article.objects.all().count()
    return "total_articles={}".format(output)

if __name__ == '__main__':
    main()
