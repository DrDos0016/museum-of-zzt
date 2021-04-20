import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402


def main():
    while True:
        id = int(input("ID: "))
        a = Article.objects.get(pk=id)
        print(a.title)
        year = str(a.publish_date)[:4]

        #find = input("FIND: ")
        #replace = input("REPLACE: ")
        find = "/static/images/mtp/"

        a = Article.objects.get(pk=id)
        a.content = a.content.replace(find, "/static/articles/" + year + "/" + a.static_directory + "/")
        a.save()
        print("Ok!")

    return True


if __name__ == '__main__':
    main()
