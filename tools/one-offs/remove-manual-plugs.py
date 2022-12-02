import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("Find articles with {% patreon_plug %} and remove them, setting the database value instead.")
    input("Press Enter to begin. This will impact the database.")
    qs = Article.objects.all().order_by("id")
    for a in qs:
        if a.pk == 324:  # Put mid article deliberately for a gag
            continue
        pos = a.content.find("patreon_plug")
        if pos != -1:
            print(a)
            a.content = a.content.replace("{% patreon_plug %}", "")
            a.save()
    return True


if __name__ == '__main__':
    main()
