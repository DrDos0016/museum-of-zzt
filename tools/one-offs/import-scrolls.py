import os
import sys

import django

from discord.constants import SCROLLS

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("This script will convert scrolls from discord/constants.py")
    print("To DB stored Scroll objects.")
    input("Press Enter to begin")

    num = 1
    for item in SCROLLS:
        src = item["source"].replace("https://museumofzzt.com", "")
        s = Scroll(
            identifier=num,
            content=item["text"],
            source=src,
            published=True
        )
        s.save()
        num += 1
        print("SAVED", s)

    return True


if __name__ == '__main__':
    main()
