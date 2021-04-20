import glob
import os
import shutil
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402


def main():
    qs = Article.objects.all()

    old = glob.glob("/var/projects/museum/museum_site/static/images/articles/previews/*.png")

    nums = []
    for i in old:
        head = os.path.basename(i).split(".")[0]
        try:
            nums.append(int(head))
        except:
            continue

    for a in qs:
        if a.id in nums:
            print(a.id, a.title, a.static_directory)
            dst = os.path.join("/var/projects/museum/museum_site/static/", a.path(), "preview.png")
            try:
                shutil.move("/var/projects/museum/museum_site/static/images/articles/previews/{}.png".format(a.id), dst)
            except FileNotFoundError:
                print("FAILED ON", a.id, a.title)


    return True


if __name__ == '__main__':
    main()
