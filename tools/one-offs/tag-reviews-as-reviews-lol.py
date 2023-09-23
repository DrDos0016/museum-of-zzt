import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("Running this script will take all Review objects (Feedback), and add the tag 'Review' to them provided they have no tags")
    input("Press Enter to begin")

    qs = Review.objects.all()
    tag = Feedback_Tag.objects.get(title="Review")

    for r in qs:
        if r.tags.all().count() == 0:
            r.tags.add(tag.pk)
            print("Tagged", r)
    print("DONE.")
    return True


if __name__ == '__main__':
    main()
