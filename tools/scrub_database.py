import datetime

import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.sessions.models import Session  # noqa: E402
from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402
from museum_site.constants import (
    REMOVED_ARTICLE, DETAIL_REMOVED, UPLOAD_CONTACT_NONE)  # noqa: E402


def main():
    print("WARNING! THIS WILL PERMANENTLY REMOVE DATA FROM THIS DATABASE")
    print("Are you sure you wish to remove all non-public data?")
    confirm = input("Type 'yes' to confirm: ")

    if confirm == "yes":
        print("Deleting removed articles...")
        for a in Article.objects.filter(published=REMOVED_ARTICLE):
            print(a)
            a.delete()
        print("Done!")
        print("Deleting removed file objects...")
        for f in File.objects.filter(details__id=DETAIL_REMOVED):
            print(f)
            f.delete()
        print("Done!")
        print("Blanking file objects...")
        for f in File.objects.all():
            f.uploader_ip = None
            f.save()

        print("Blanking review objects...")
        for r in Review.objects.all():
            r.email = ""
            r.ip = ""
            r.save()
        print("Done!")
        print("Blanking upload objects...")
        for u in Upload.objects.all():
            u.email = ""
            u.edit_token = ""
            u.ip = ""
            u.notes = "Blanked notes."
            u.contact = UPLOAD_CONTACT_NONE
            u.contacted = False
            u.save()
        print("Done!")

        print("Deleting sessions...")
        Session.objects.all().delete()
        print("Done!")
        print("Blanking user accounts...")
        qs = User.objects.all()
        for u in qs:
            u.username = "USER #" + str(u.id)
            u.first_name = ""
            u.last_name = ""
            u.email = "test@example.com"
            u.password = u.set_password("password")
            u.is_staff = False
            u.is_superuser = False
            u.save()

        print("Private data has removed. Database can be publicly shared.")
        print("DONE.")
    else:
        print("ABORTED.")


if __name__ == '__main__':
    main()
