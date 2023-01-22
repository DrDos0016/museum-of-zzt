import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("This script will replace calls to old {% gblock %} tag with modern {% model_block %} tags across all articles.")
    print("EXCEPT: PK#563 Best of ZZT Part 2 and PK#585: The NL ZZT/MZX Newsletter Archive")
    input("Press ENTER to begin. This will modify the database.")
    qs = Article.objects.all()
    to_update = []
    for a in qs:
        if a.pk in [563, 585]:  # Exceptions listed above
            continue

        if "{% gblock" in a.content:
            to_update.append(a)

    print("Found {} articles to update".format(len(to_update)))

    for a in to_update:
        print(a.title)
        # {% gblock files.3748 "gallery" %} -> {% model_block c view="gallery" %}
        # {% gblock file %} -> {% model_block file %}
        a.content = a.content.replace("{% gblock ", "{% model_block ")
        a.content = a.content.replace('"gallery" %}', 'view="gallery" %}')
        a.save()

    return True


if __name__ == '__main__':
    main()
