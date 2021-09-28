import datetime
import os
import sys

import django
django.setup()

from django.contrib.sessions.models import Session  # noqa: E402


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    count = 0
    idx = 1

    qs = Session.objects.all()

    print("Deleting sessions with expiration dates prior to", now)

    for s in qs:
        if s.expire_date < now:
            s.delete()
            count += 1
        idx += 1

    print("Deleted", count, "sessions.")
    print(Session.objects.count(), "sessions are active.")
    return True


if __name__ == "__main__":
    main()
