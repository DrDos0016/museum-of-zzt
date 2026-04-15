import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    # Update some existing articles to use the newly created "Gamedev" category rather than "Livestream"
    pks = [
        453, 454, 455, 456, 457, 460, 463, 465, 469, 477,  # Joy
        # Hahol never got a Museum article!!!!
        1039,  # Regumprement
        1112, 1118,  # Learning To Weave
        1148, 1184, 1210, # 100 Ammo / Alien Office / Bomb With Me
        1300, 1307, 1311  # Darby-like (P1+2, P3, P4)
    ]
    qs = Article.objects.filter(pk__in=pks)
    for a in qs:
        a.category = "Gamedev"
        a.save()
        print("Set", a, "to Gamedev category.")
    return True


if __name__ == '__main__':
    main()
