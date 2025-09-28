import codecs
import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402
from museum.settings import *  # noqa: E402


def main():
    ROOT = os.path.join(BASE_DIR, "tools/one-offs/nl/")
    issues = ["nlv4_1.txt", "nlv4_2.txt", "nlv4_3.txt", "nlv4_5.txt", "nlv4_6.txt", "nlv4_7.txt"]

    """
    if ENVIRONMENT == "DEV":
        print("This is DEV so let me delete any previously botched imports")
        qs = Article.objects.filter(pk__gte=1239).order_by("id")
        for a in qs:
            print("DELETING", a)
            a.delete()

        print("All cleaned up.")
    """

    # Some actual work
    titles = {
        "nlv4_1.txt": "The NL - Volume 4 Issue 1 (The New Year's Issue)",
        "nlv4_2.txt": "The NL - Volume 4 Issue 2 (The Newzlamer Issue)",
        "nlv4_3.txt": "The NL - Volume 4 Issue 3 (The St. Patrick Issue)",
        "nlv4_5.txt": "The NL - Volume 4 Issue 5 (The May Sweeps)",
        "nlv4_6.txt": "The NL - Volume 4 Issue 6 (The Summer Bash Issue)",
        "nlv4_7.txt": "The NL - Volume 4 Issue 7 (The Summer End Issue)",
    }
    descriptions = {
        "nlv4_1.txt": "Inside - The ZOP Stop, The Critic Corner",
        "nlv4_2.txt": "Inside - The NL Column About Nothing In Particular III, The Critic Corner",
        "nlv4_3.txt": "Inside - Sorve: First Blood Preview, Zmenu Advertisement, The NL Column About Nothing In Particular IV, Surprise Software Update, The Critic Corner",
        "nlv4_5.txt": "A Picture, The Critic Corner",
        "nlv4_6.txt": "Company News, The Critic Corner",
        "nlv4_7.txt": "What's The Problem?!, The Critic Corner",
    }
    dates = {
        "nlv4_1.txt": "1997-01-31",
        "nlv4_2.txt": "1997-02-28",
        "nlv4_3.txt": "1997-03-31",
        "nlv4_5.txt": "1997-05-31",
        "nlv4_6.txt": "1997-07-31",
        "nlv4_7.txt": "1997-08-30",
    }

    for issue in issues:
        a = Article(
            title=titles.get(issue, "BAD TITLE"), author="Various", category="Historical", schema="80col",
            published=Article.PUBLISHED, description=descriptions.get(issue, "BAD DESC"),
            allow_comments=True, spotlight=False, static_directory="the-nl",
            publish_date=dates.get(issue),
        )
        with codecs.open(ROOT + issue, encoding="cp437") as fh:
            content = fh.read()
            a.content = content
        a.save()
        print("SAVED", a)


    return True


if __name__ == '__main__':
    main()
