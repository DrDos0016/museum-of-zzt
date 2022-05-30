import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402


def main():
    print("This script will associate a list of Files to an Article.")
    print("Enter a blank value to quit.")

    print("1: Manual Entry of Data")
    print("2: Pre-formatted File")
    choice = input("Choice: ")

    if choice == "":
        sys.exit()

    if choice == "1":
        while True:
            a_pk = input("Enter PK of article: ")
            if a_pk == "":
                break

            a_pk = int(a_pk)

            a = Article.objects.filter(pk=a_pk).first()
            if not a:
                print("No article found")
                continue

            print(a.title)
            f_pks = input("Enter comma separated list of File PKs to associate: ")
            if f_pks == "":
                break

            f_pks = f_pks.replace(" ", "").split(",")
            zfile_filter = []

            for f in f_pks:
                zfile_filter.append(int(f))

            qs = File.objects.filter(pk__in=zfile_filter)

            if len(qs) != len(zfile_filter):
                print(
                    "WARNING: LENGTH MISMATCH. QUERYSET: {} REQUESTED: {}".format(
                        len(qs), len(zfile_filter)
                    )
                )

            print("Working with article:", a.title)
            for f in qs:
                print(f.title)

            confirm = input("Type 'yes' to add associations: ")

            if confirm == "yes":
                for f in qs:
                    f.articles.add(a)
                    f.article_count += 1
                    f.save()

            print("Associations added for article.")
    elif choice == "2":
        print("Pre-formatted files should contain lines that look like this:")
        print("123:merbotia,esp,mercenary")
        print("The PK of the article, and then a list of file keys that should be associated with the article")
        filename = input("Enter filename to use: ")

        with open(filename) as fh:
            for line in fh.readlines():
                if not line:
                    break

                (pk, keys) = line.strip().split(":")
                pk = int(pk)
                keys = keys.split(",")

                a = Article.objects.filter(pk=pk).first()
                if not a:
                    print("No article found with PK {}".format(pk))
                    continue
                else:
                    print("Working with article:", a.title)

                for key in keys:
                    f = File.objects.get(key=key)
                    f.articles.add(a)
                    f.article_count += 1
                    f.save()
                    print("Added association for", f.title)


    return True


if __name__ == '__main__':
    main()
