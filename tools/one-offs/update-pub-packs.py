import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    replacement = "<h2>{% zfile_citation file %}</h2>"
    print("This script updates the headings used in (most) old Publication Packs to use the ZFile Citation template tag instead")
    input("Press ENTER to begin.")

    qs = Article.objects.all().order_by("-pk")
    print(len(qs), "articles in consideration.")

    for a in qs:
        og = a.content
        updated = a.content.replace("<h2>{{file.citation_str}}</h2>", replacement)
        updated = updated.replace('<h2>"{{file.title}}" {% if not file.author_unknown %}by {{file.author_list|join:", "}}{% endif %}{% if file.release_date %} ({{file.release_date.year}}){% endif %}</h2>', replacement)
        updated = updated.replace('<h2>"{{file.title}}" {% if file.author != "Unknown" %}by {{file.author}}{% endif %}{% if file.release_date %} ({{file.release_date.year}}){% endif %}</h2>', replacement)
        updated = updated.replace('<h2>"{{file.title}}" {% if file.author != "Unknown" %} by {{file.author}}{% endif %}{% if file.release_date %} ({{file.release_date.year}}){% endif %}</h2>', replacement)

        if og != updated:
            a.content = updated
            print("UPDATED ARTICLE", a)
            a.save()


    return True


if __name__ == '__main__':
    main()
