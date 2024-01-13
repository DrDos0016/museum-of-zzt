import glob
import json
import os
import sys
import urllib.request
import zipfile

from datetime import datetime

import django
import requests

django.setup()

from museum_site.constants import DATA_PATH  # noqa: E402
from museum_site.models import *  # noqa: E402
from museum_site.core.detail_identifiers import *  # noqa: E402
from museum_site.core.file_utils import calculate_md5_checksum  # noqa: E402

TEST_ARCHIVE_LINKS = True if "iatest" in sys.argv else False


def main():
    qs = File.objects.all().order_by("-id")
    all_issues = []
    output = {
        "meta": {
            "started": str(datetime.now()),
        }
    }
    for zf in qs:
        print(zf.id)
        issues = scan(zf)

        if issues:
            issues["pk"] = zf.pk

        all_issues.append(issues)

    output["issues"] = all_issues
    output["meta"]["finished"] = str(datetime.now())

    with open(os.path.join(DATA_PATH, "scan.json"), "w") as fh:
        fh.write(json.dumps(output))

    return True


def scan(zfile):
    issues = {}
    exists = True
    checksummed = True

    # Pull detail list
    details = zfile.details.all()
    detail_list = []
    for detail in details:
        detail_list.append(detail.id)

    """ Used for Museum Scan to identify basic issues """
    # Validate letter
    if zfile.letter not in "1abcdefghijklmnopqrstuvwxyz":
        issues["letter"] = "Invalid letter: '{}'".format(zfile.letter)
    if not os.path.isfile(zfile.phys_path()):
        issues["missing_file"] = "File not found: '{}'".format(zfile.phys_path())
        exists = False
    if not zfile.sort_title:
        issues["sort_title"] = "Sort title not set."
    if exists and zfile.size != os.path.getsize(zfile.phys_path()):
        issues["size_mismatch"] = "DB size doesn't match physical file size: {}/{}".format(zfile.size, os.path.getsize(zfile.phys_path()))
    if zfile.release_date and zfile.release_date.year < 1991:
        issues["release_date"] = "Release date is prior to 1991."
    if zfile.release_date and zfile.release_source == "":
        issues["release_date_source"] = "Release source is blank, but release date is set."
    if not zfile.has_preview_image:
        if (DETAIL_LOST not in detail_list) and (DETAIL_ZZM not in detail_list):
            issues["preview_image"] = "No preview image."
    if zfile.has_preview_image and (not os.path.isfile(zfile.screenshot_phys_path())):
        issues["preview_image_missing"] = "Screenshot does not exist at {}".format(zfile.preview_url())

    # All Feedback
    feedback = Review.objects.for_zfile(zfile.id)
    feedback_len = len(feedback)
    if feedback_len != zfile.feedback_count:
        issues["feedback_count"] = "Feedback count in DB does not match 'feedback_count': {}/{}".format(feedback_len, zfile.feedback_count)

    # Review related
    reviews = Review.objects.for_zfile(zfile.id).filter(tags__key="reviews")
    rev_len = len(reviews)
    if rev_len != zfile.review_count:
        issues["review_count"] = "Review count in DB do not match 'review_count': {}/{}".format(rev_len, zfile.review_count)

    # Confirm LOST does not exist
    if DETAIL_LOST in detail_list and exists:
        issues["not_lost"] = "File is marked as 'Lost', but a Zip exists."

    articles = zfile.articles.accessible()
    article_len = len(articles)
    if article_len != zfile.article_count:
        issues["article_count"] = "Articles in DB do not match 'article_count': {}/{}".format(article_len, zfile.article_count)

    if not zfile.checksum:
        issues["blank_checksum"] = "Checksum not set."
        checksummed = False

    # Calculate file's checksum
    md5 = calculate_md5_checksum(zfile.phys_path())
    if checksummed and (zfile.checksum != md5):
        issues["checksum_mismatch"] = "Checksum in DB does not match calculated checksum: {} / {}".format(zfile.checksum, md5)

    # Board counts
    if (DETAIL_ZZT in detail_list) and zfile.playable_boards is None:
        issues["playable_boards"] = "File has no playable boards value but is marked as ZZT"

    if (DETAIL_ZZT in detail_list) and zfile.total_boards is None:
        issues["total_boards"] = "File has no total boards value but is marked as ZZT"

    if zfile.archive_name == "" and (DETAIL_LOST not in detail_list and DETAIL_UPLOADED not in detail_list):
        issues["archive_mirror"] = "File has no archive.org mirror"

    # Contents in DB vs Contents in zip
    db_contents = zfile.content.all()
    crcs = []
    for i in db_contents:
        crcs.append(i.crc32)

    zf = None
    try:
        zf = zipfile.ZipFile(zfile.phys_path())
    except (zipfile.BadZipFile, FileNotFoundError):
        zf = None

    if zf is not None:
        for zi in zf.infolist():
            if str(zi.CRC) not in crcs:
                issues["content_error"] = "File's Contents object does not match ZipInfo"
                break

    return issues


if __name__ == "__main__":
    main()
