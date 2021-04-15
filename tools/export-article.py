import os
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print("Export single article: export-article.py <article_id>")
        print("Export all articles: export-article.py A")
        return False

    if sys.argv[1] == "A":
        qs = Article.objects.all()
    else:
        qs = Article.objects.filter(pk=int(sys.argv[1]))

    root_path = input("Output path (blank for current dir): ")

    if root_path:
            os.mkdir(root_path)

    for a in qs:
        path = os.path.join(root_path, str(a.id) + ".html")
        with open(path, "w") as fh:
            fh.write("<!-- [{}] {} -->\n".format(a.id, a.title))
            fh.write("<!-- Author: {} -->\n".format(a.author))
            fh.write("<!-- Category: {} -->\n".format(a.category))
            fh.write("<!-- Schema: {} -->\n".format(a.schema))
            fh.write("<!-- Published/Date: {} {} -->\n".format(a.published, a.publish_date))
            fh.write("<!-- Static Dir: {} -->\n".format(a.static_directory))
            fh.write("<!-- Preview: {} -->\n".format(a.preview))
            fh.write("<!-- Summary: {} -->\n".format(a.summary))
            fh.write("<!-- CSS BEGIN -->\n")
            fh.write(a.css + "\n")
            fh.write("<!-- CSS END -->\n")
            fh.write("<!-- CONTENT BEGIN -->\n")
            fh.write(a.content + "\n")
            fh.write("<!-- CONTENT END -->\n")

        print("Wrote", path)
    return True


if __name__ == '__main__':
    main()
