import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    to_replace = [
        (1, 45), # adam r.
        (3, 55), # alan z.
        (4, 65), # allen p.
        (2, 52), # al p.
        (12, 1255), # asie
        (5, 130), # beth d.
        (6, 301), # david b.
        (8, 733), # matt w.
        (9, 988), # scott h.
        (10, 1027), # snorb
        (1378, 1113), # tim s.
        (11, 1154), # various
    ]

    for ids in to_replace:
        old = ids[0]
        new = ids[1]
        qs = File.objects.filter(authors__id=old)
        for zf in qs:
            print("Updating", zf)
            print("Adding", new)
            zf.authors.add(new)
            print("Removing", old)
            zf.authors.remove(old)
        Author.objects.filter(pk=old).delete()
        print("Erasing bad author")
        print("---")


    return True


if __name__ == '__main__':
    main()
