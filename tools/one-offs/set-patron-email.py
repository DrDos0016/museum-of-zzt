import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User

from museum_site.models import *  # noqa: E402


def main():
    print(
        "Run to set profile.patron_email to user.email when "
        "profile.patron_email is blank."
    )
    save_changes = input("Type 'yes' to make changes. Leave blank to discard. ")

    if save_changes == "yes":
        save_changes = True
    else:
        save_changes = False

    qs = Profile.objects.filter(patron_email="").prefetch_related("user")

    for p in qs:
        p.patron_email = p.user.email
        print(p.user.username, "patron_email now", p.user.email)
        if save_changes:
            p.save()

    print("DONE.")
    return True


if __name__ == '__main__':
    main()
