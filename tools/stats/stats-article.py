import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

NEW_YEAR = 2025
OLD_YEAR = 2024


def main():
    category_word_and_article_counts()  # Article Word Counts / Article Counts by category
    cl_year_spread()  # Release Years of ZFiles covered in completed year's Closer Looks

    zfiles_with_without_feedback_articles()  # Files with/without feedback/articles
    livestream_year_spread()  # Release years of livestreamed ZFiles

    # File counts for each year broken into "2023" and "Previous"

    # stats.log
    # Upload Queue Size By Date
    # Total Files
    # Total Authors/Companies
    parse_nightly_stats()
    return True


def category_word_and_article_counts():
    qs = Article.objects.filter(publish_date__gte="{}-01-01".format(OLD_YEAR), publish_date__lt="{}-01-01".format(NEW_YEAR))
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
    print("-" * 60)
    return True

def cl_year_spread():
    print("=" * 80)
    print("CLOSER LOOK SPREAD")
    """ Release year for assoc. ZFiles with Closer Look articles """
    qs = Article.objects.filter(publish_date__gte="{}-01-01".format(OLD_YEAR), publish_date__lt="{}-01-01".format(NEW_YEAR), category="Closer Look")
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
    print("-" * 60)
    return True

def parse_nightly_stats():
    with open("{}-stats.log".format(OLD_YEAR)) as fh:
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
    print("-" * 60)
    return True


def zfiles_with_without_feedback_articles():
    print("ZFiles with/without feedback/articles")
    counts = {"with_feedback": 0, "without_feedback": 0, "with_articles": 0, "without_articles": 0, "with_non_pp_articles": 0, "without_non_pp_articles": 0}
    qs = File.objects.all()
    for zf in qs:
        counts["with_feedback"] += (1 if zf.feedback_count else 0)
        counts["without_feedback"] += (1 if not zf.feedback_count else 0)

        to_inc = {"with_articles": False, "without_articles": True, "with_non_pp_articles": False, "without_non_pp_articles": True}
        for a in zf.articles.all():
            if a.category == "Publication Pack":
                to_inc["with_articles"] = True
                to_inc["without_articles"] = False
            else:
                to_inc["with_non_pp_articles"] = True
                to_inc["without_non_pp_articles"] = False
                to_inc["with_articles"] = True
                to_inc["without_articles"] = False

        for k, v in to_inc.items():
            if v == True:
                counts[k] += 1


    for k, v in counts.items():
        print("{};{}".format(k, v))
    print("-" * 60)
    return True

def livestream_year_spread():
    print("ZGames streamed, grouped by release year -- NOTE THIS ASSUMES ALL VODS WERE PUBLISHED BEFORE YEAR'S END")
    article_pks = list(
        Article.objects.filter(category="Livestream", publish_date__gte="{}-01-01".format(OLD_YEAR), publish_date__lt="{}-01-01".format(NEW_YEAR)).values_list("pk", flat=True)
    )
    qs = File.objects.filter(articles__in=article_pks).order_by("release_date")
    counts = {}
    for zf in qs:
        year = zf.release_year(default="Unknown")
        counts[year] = counts.get(year, 0) + 1

    for k,v in counts.items():
        print("{};{}".format(k, v))
    print("-" * 60)
    return True

if __name__ == '__main__':
    main()
