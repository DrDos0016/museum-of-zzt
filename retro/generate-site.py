import glob
import os
import sys

import django

from django.shortcuts import render

django.setup()

from django.contrib.auth.models import User

from museum_site.models import *  # noqa: E402
from museum_site.constants import SITE_ROOT
from museum_site.core.detail_identifiers import DETAIL_UPLOADED


def main():
    template_path = os.path.join(SITE_ROOT, "retro", "components", "template.html")
    component_path = os.path.join(SITE_ROOT, "retro", "components")
    retro_path = os.path.join(SITE_ROOT, "retro")
    with open(template_path) as fh:
        base = fh.read()
    print("Loaded main template.")
    print("Generating index.html... ", end="")

    # Index
    with open(os.path.join(component_path, "block-index.html")) as fh:
        content = fh.read()
    rendered = base.replace("{TITLE}", "Index")
    rendered = rendered.replace("{CONTENT}", content)
    with open(os.path.join(retro_path, "index.html"), "w") as fh:
        fh.write(rendered)
    print("OK")

    # Letters
    for letter in "1abcdefghijklmnopqrstuvwxyz":
        print("Generating {}.html...".format(letter), end="")

        files = File.objects.filter(letter=letter).exclude(details__id__in=[DETAIL_UPLOADED]).distinct().order_by("sort_title")
        table_rows = ""
        for f in files:
            table_rows += ("<tr>\n"
            "<td><a href=\"{}\">{}</a></td>\n"
            "<td>{}</td>\n"
            "<td>{}</td>\n"
            "<td>{}</td>\n"
        "</tr>\n").format(
            f.download_url(),
            f.title,
            ", ".join(f.related_list("authors")),
            round(f.size / 1024, 2),
            ", ".join(f.genre_list())
        )

        with open(os.path.join(component_path, "block-file-list.html")) as fh:
            content = fh.read()
            content = content.replace("{TABLE_ROWS}", table_rows)

        rendered = base.replace("{TITLE}", letter.upper())
        rendered = rendered.replace("{CONTENT}", content)
        with open(os.path.join(retro_path, letter + ".html"), "w") as fh:
            fh.write(rendered)

        print ("OK")

    # Upload Queue
    print("Generating uploaded.html...", end="")

    files = File.objects.filter(details__id__in=[DETAIL_UPLOADED]).distinct().order_by("sort_title")
    table_rows = ""
    for f in files:
        table_rows += ("<tr>\n"
        "<td><a href=\"{}\">{}</a></td>\n"
        "<td>{}</td>\n"
        "<td>{}</td>\n"
        "<td>{}</td>\n"
    "</tr>\n").format(
        f.download_url(),
        f.title,
        ", ".join(f.related_list("authors")),
        round(f.size / 1024, 2),
        ", ".join(f.genre_list())
    )

    with open(os.path.join(component_path, "block-file-list.html")) as fh:
        content = fh.read()
        content = content.replace("{TABLE_ROWS}", table_rows)

    rendered = base.replace("{TITLE}", "Upload Queue")
    rendered = rendered.replace("{CONTENT}", content)
    with open(os.path.join(retro_path, "uploaded.html"), "w") as fh:
        fh.write(rendered)

    print ("OK")
    return True


if __name__ == '__main__':
    main()
