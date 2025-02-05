import os
import sys

import django

from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("This script will find all publication packs (and articles #651/#653)")
    print("It will then replace the image set divs with a new template tag.")
    print("This WILL update live data in the database. It can be run multiple times safely.")
    qs = list(Article.objects.filter(category="Publication Pack").order_by("id")) + list(Article.objects.filter(pk__in=[651, 563]))
    for a in qs:
        print(a.title, end=" ")
        did_something = False
        soup = BeautifulSoup(a.content, "html.parser")

        for tag in soup.find_all("div", {"class": "image-set"}):
            did_something = True
            # Find the image names
            raw = str(tag)
            image_list = []  # "1.png", "2.png", etc.
            for line in raw.split("\n"):
                start = line.find(":") + 2
                if (start == 1): # -1 + 2 for no match
                    continue

                #print(line)
                line = line[start:]
                end = line.find('"')
                line = line[:end]
                image_list.append(line)

            #print(image_list)
            images = ""
            for i in image_list:
                images += "'{}' ".format(i)
            images = images.strip()
            tag.replaceWith("{% image_set " + images + " %}")
            #print("================")


        """
        with open("test.txt", "w") as fh:
            final = str(soup).replace("<br/>", "<br>")  # Absolutely not.
            fh.write(str(soup))
        #print(soup)
        """
        if did_something:
            a.content = str(soup).replace("<br/>", "<br>")  # Absolutely not.
            a.save()
            print("UPDATED")
        else:
            print("NO CHANGES")

    return True


if __name__ == '__main__':
    main()
