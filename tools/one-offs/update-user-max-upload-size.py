import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402
from museum_site.constants import UPLOAD_CAP


def main():
    qs = Profile.objects.all().order_by("user_id")
    count = 0
    for p in qs:
        if p.max_upload_size < UPLOAD_CAP:
            p.max_upoad_size = UPLOAD_CAP
            p.save()
            count += 1

    print("Raised upload limit for {} users.".format(count))
    return True


if __name__ == '__main__':
    main()
