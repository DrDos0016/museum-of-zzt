import os
import sys

import django

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *
from museum_site.common import *
from museum_site.constants import *


def main():
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

    return True


if __name__ == "__main__":
    main()
