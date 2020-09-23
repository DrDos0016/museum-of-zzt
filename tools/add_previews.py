import os
import sys

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402
from museum_site.common import *  # noqa: E402
from museum_site.constants import *  # noqa: E402

HELP = """This script will list all articles without a preview image.
If a PNG matched the article's PK is in static/images/articles/previews it
will automatically be assigned.

Press ENTER to begin."""


def main():
    input(HELP)

    articles = Article.objects.filter(preview="").order_by("id")

    for a in articles:
        path = os.path.join(
            SITE_ROOT, "museum_site/static/images/articles/previews/{}.png"
        )
        preview_path = path.format(a.id)
        if os.path.isfile(preview_path):
            print("[X]", a.id, a.title, preview_path)
            a.preview = "articles/previews/{}.png".format(a.id)
            a.save()
        else:
            print("[ ]", a.id, a.title)

    print("Done.")
    return True


if __name__ == "__main__":
    main()
