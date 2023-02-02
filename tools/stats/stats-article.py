import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():


    #category_word_and_article_counts()
    cl_year_spread()

    # stats.log
    #parse_nightly_stats()
    return True


def category_word_and_article_counts():
    qs = Article.objects.filter(publish_date__gte="2022-01-01", publish_date__lt="2023-01-01")
    category_word_counts = {}
    category_article_counts = {}
    for a in qs:
        if category_word_counts.get(a.category):
            category_word_counts[a.category] += a.word_count()
            category_article_counts[a.category] += 1
        else:
            category_word_counts[a.category] = a.word_count()
            category_article_counts[a.category] = 1
        print(a.category, a.title)

    print("CATEGORY WORD COUNTS")
    for k, v in category_word_counts.items():
        print(k + ";" + str(v))

    print("CATEGORY ARTICLE COUNTS")
    for k, v in category_article_counts.items():
        print(k + ";" + str(v))

def cl_year_spread():
    print("=" * 80)
    print("CLOSER LOOK SPREAD")
    """ Release year for assoc. ZFiles with Closer Look articles """
    qs = Article.objects.filter(publish_date__gte="2022-01-01", publish_date__lt="2023-01-01", category="Closer Look")
    years = {}
    for a in qs:
        zfqs = File.objects.filter(articles__pk=a.pk)
        for zf in zfqs:
            print(zf.title, zf.release_year())
            if years.get(zf.release_year(default="Unknown")):
                years[zf.release_year()] += 1
            else:
                years[zf.release_year()] = 1

    for k, v in years.items():
        print(k + ";" + str(v))

def parse_nightly_stats():
    with open("/var/projects/museum-of-zzt/museum_site/static/data/2022-stats.log") as fh:
        print("Date;Queue Size;Total Files;Historic Files;Modern Files;This Year Historic Files;Authors;Companies;Total Articles")
        for line in fh.readlines():
            line = line.strip()
            if not line:
                continue
            info = line.split("|")
            row = {
                "date_str": info[0].split("=")[-1],
                "queue_size": info[1].split("=")[-1],
                "total_files": info[2].split("=")[-1],
                "historic_files": info[3].split("=")[-1],
                "modern_files": info[4].split("=")[-1],
                "this_year_historic_files": info[5].split("=")[-1],
                "authors": info[6].split("=")[-1],
                "companies": info[7].split("=")[-1],
                "total_articles": info[8].split("=")[-1],
            }
            print(
                row["date_str"] + ";" + row["queue_size"] + ";" + row["total_files"] + ";" + row["historic_files"] + ";" + row["modern_files"] + ";" +
                row["this_year_historic_files"] + ";" + row["authors"] + ";" + row["companies"] + ";" + row["total_articles"]
            )

if __name__ == '__main__':
    main()
