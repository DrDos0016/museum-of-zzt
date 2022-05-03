import json
import urllib.parse
import requests

from museum_site.constants import *
from museum_site.common import record
from museum_site.private import NEW_REVIEW_WEBHOOK_URL, NEW_UPLOAD_WEBHOOK_URL


def discord_announce_review(review, env=None):
    if env is None:
        env = ENV

    if env != "PROD":
        record("# DISCORD ANNOUNCEMENT SUPPRESSED DUE TO NON-PROD ENVIRONMENT")
        return False

    preview_url = HOST + "static/" + urllib.parse.quote(
         review.zfile.screenshot_url()
    )

    discord_post = (
        "*A new review for {} has been posted!*\n"
        "**{}** written by {}\n"
        "Read: https://museumofzzt.com{}#rev-{}\n"
    ).format(
        review.zfile.title, review.title, review.get_author(),
        urllib.parse.quote(review.zfile.review_url()), review.id
    )

    discord_data = {
        "content": discord_post,
        "embeds": [{"image": {"url": preview_url}}]
    }
    resp = requests.post(
        NEW_REVIEW_WEBHOOK_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(discord_data)
    )
    return True


def discord_announce_upload(upload, env=None):
    if upload.announced:
        return False

    if env is None:
        env = ENV

    if env != "PROD":
        record("# DISCORD ANNOUNCEMENT SUPPRESSED DUE TO NON-PROD ENVIRONMENT")
        upload.announced = True
        upload.save()
        return False

    zfile = upload.file

    preview_url = HOST + "static/" + urllib.parse.quote(
         zfile.screenshot_url()
    )

    if zfile.release_date:
        year = " ({})".format(str(zfile.release_date)[:4])
    else:
        year = ""
    discord_post = (
        "*A new item has been uploaded to the Museum queue!*\n"
        "**{}** by {}{}\n"
        "Explore: https://museumofzzt.com{}\n"
    ).format(
        zfile.title, zfile.author,
        year,
        urllib.parse.quote(zfile.file_url())
    )

    discord_data = {
        "content": discord_post,
        "embeds": [{"image": {"url": preview_url}}]
    }
    resp = requests.post(
        NEW_UPLOAD_WEBHOOK_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(discord_data)
    )

    upload.announced = True
    upload.save()
    return True
