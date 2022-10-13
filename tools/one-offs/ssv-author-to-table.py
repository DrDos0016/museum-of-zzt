import os
import sys

import django

from django.template.defaultfilters import slugify

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print(
        "This script will analyze all File objects author value. "
        "It will then create Author model objects for all found author names"
    )
    input("Press Enter to begin")

    qs = File.objects.all().order_by("id")

    all_author_names = []
    for zf in qs:
        authors = zf.author.split("/")

        for author in authors:
            if author:
                all_author_names.append(author)

    all_author_names.sort()
    author_names = []
    last = "X!Y!Z!Z!Y"
    for a in all_author_names:
        if a == last:
            continue
        author_names.append(a)
        last = a

    created_count = 0
    for a in author_names:
        # Try and come up with a sensible slug
        (a_obj, created) = Author.objects.get_or_create(title=a, slug=slugify(a))
        created_count += 1 if created else 0

        # Some unique author names
        a_obj.save()

    print("Created {} author objects.".format(created_count))
    print("Associating authors with zfiles...")
    qs = File.objects.all().order_by("id")

    association_count = 0
    for zf in qs:
        authors = zf.author.split("/")
        for author in authors:
            if author:
                zf.authors.add(Author.objects.filter(title=author).order_by("id").first())
                association_count += 1

    print("Added {} associations.".format(association_count))
    print("DONE.")
    return True


if __name__ == '__main__':
    main()
