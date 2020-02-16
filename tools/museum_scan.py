import glob
import os
import sys
import urllib.request

import django
import requests

sys.path.append("/var/projects/museum/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from museum_site.models import *
from museum_site.common import *


TEST_ARCHIVE_LINKS = True if "iatest" in sys.argv else False
IGNORE_LIST = (

)


def main():
    files = File.objects.all().order_by("-id")
    for f in files:
        if f.id in IGNORE_LIST:
            continue

        issues = field_check(f)

        if len(issues["warnings"]) != 0 or len(issues["errors"]) != 0:
            print("<hr><b><a href='{}'>{}</a> - <a href='/admin/museum_site/file/{}/change/'>Edit</a> - <a href='/tools/{}'>Tools</a></b>\n".format(f.file_url(), f, f.id, f.id))
            print("<ul>\n")
            for w in issues["warnings"]:
                print("<li class='warning'>{}</li>\n".format(w))
            for e in issues["errors"]:
                print("<li class='error'>{}</li>\n".format(e))
            print("</ul>\n")


    return True


def field_check(f):
    exists = True
    issues = {"warnings": [], "errors": []}

    # Validate letter
    if f.letter not in LETTERS:
        issues["errors"].append("Invalid letter '{}'".format(f.letter))

    # Validate filename exists
    if not os.path.isfile(f.phys_path()):
        exists = False
        issues["errors"].append("FILE DOES NOT EXIST AT '{}'".format(f.phys_path()))

    if not f.sort_title:
        issues["warnings"].append("Sort title not set.")

    """
    if exists and f.size != os.path.getsize(f.phys_path()):
        issues["warnings"].append("File size doesn't match physical file: {}/{}".format(f.size, os.path.getsize(f.phys_path())))
    """

    if "," in f.author:
        issues["warnings"].append("Comma in author. Should be slash?")

    if "," in f.genre:
        issues["warnings"].append("Comma in genre. Should be slash.")

    if f.release_date and f.release_date.year < 1991:
        issues["warnings"].append("Release date is prior to 1991.")

    if f.release_date and f.release_source == "":
        issues["warnings"].append("Release source is blank, but release date is set.")

    if f.screenshot == "":
        issues["warnings"].append("No screenshot.")

    if f.screenshot and (not os.path.isfile(os.path.join(STATIC_PATH, f.screenshot_url()))):
        issues["errors"].append("Screenshot does not exist at {}".format(f.screenshot_url()))

    if f.company == None:
        issues["warnings"].append("Company is null. Use empty string for files not published under a company.")

    # Review related
    reviews = Review.objects.filter(file_id=f.id)
    rev_len = len(reviews)
    if rev_len != f.review_count:
        issues["warnings"].append("Reviews in DB do not match 'review_count': {}/{}".format(rev_len, f.review_count))

    # Detail related
    details = f.details.all()
    detail_list = []
    for detail in details:
        detail_list.append(detail.id)

    # Confirm LOST does not exist
    if DETAIL_LOST in detail_list and exists:
        issues["warnings"].append("File is marked as 'Lost', but a Zip exists.")

    if DETAIL_CONTEST in detail_list:
        issues["warnings"].append("File is marked as 'Contest', a deprecated Detail.")

    articles = f.articles.all()
    article_len = len(articles)
    if article_len != f.article_count:
        issues["warnings"].append("Articles in DB do not match 'article_count': {}/{}".format(article_len, f.article_count))

    if not f.checksum:
        issues["warnings"].append("Checksum not set.")

    # Calculate file's checksum
    md5 = None
    try:
        resp = subprocess.run(["md5sum", f.phys_path()], stdout=subprocess.PIPE)
        md5 = resp.stdout[:32].decode("utf-8")
    except:
        pass

    if md5 and f.checksum != md5:
        issues["warnings"].append("Checksum in DB does not match calculated checksum:<br><div class='mono'>{}</div><div class='mono'>{}</div>".format(f.checksum, md5))


    # Board counts
    if (DETAIL_ZZT in detail_list or DETAIL_SZZT in detail_list) and f.playable_boards is None:
        issues["warnings"].append("File has no playable boards value but is marked as ZZT/Super ZZT")

    if (DETAIL_ZZT in detail_list or DETAIL_SZZT in detail_list) and f.total_boards is None:
        issues["warnings"].append("File has no total boards value but is marked as ZZT/Super ZZT")

    if f.archive_name == "" and (DETAIL_LOST not in detail_list and DETAIL_UPLOADED not in detail_list):
        issues["warnings"].append("File has no archive.org mirror")

    # Test functioning archive.org link
    if f.archive_name and TEST_ARCHIVE_LINKS:
        url = "https://archive.org/embed/" + f.archive_name
        resp = requests.get(url)
        if resp.status_code != 200:
            issues["warnings"].append("{} returned status {}".format(url, resp.status_code))

    # Zip related
    return issues


if __name__ == "__main__":
    main()
