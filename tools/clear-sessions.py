import datetime
import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.sessions.models import Session

from museum_site.models import *  # noqa: E402
from museum_site.constants import REMOVED_ARTICLE, DETAIL_REMOVED  # noqa: E402


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    count = 0
    idx = 1

    qs = Session.objects.all()

    print("Deleting sessions with expiration dates prior to", now)

    for s in qs:
        print(idx, s.expire_date)
        if s.expire_date < now:
            s.delete()
            count += 1
        idx += 1

    print("Deleted", count, "sessions.")
    print(Session.objects.count(), "sessions are active.")
    return True


if __name__ == "__main__":
    main()
