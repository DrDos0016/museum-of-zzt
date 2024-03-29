import json
import urllib.parse

import requests

from django.core.cache import cache

from museum_site.constants import *
from museum_site.core.misc import record
from museum_site.settings import NEW_REVIEW_WEBHOOK_URL, NEW_UPLOAD_WEBHOOK_URL, DISCORD_INVITE_URL

# Announcement Settings
ANNOUNCE_ALL = 2
ANNOUNCE_LOGGED_IN = 1
ANNOUNCE_NONE = 0
DISCORD_ANNOUNCE_UPLOADS = ANNOUNCE_ALL
DISCORD_ANNOUNCE_REVIEWS = ANNOUNCE_ALL

def discord_announce_review(review, env=None, mode="Create"):
    if env is None:
        env = ENV

    if DISCORD_ANNOUNCE_REVIEWS == ANNOUNCE_NONE:
        record("# DISCORD ANNOUNCEMENTS ARE CURRENTLY DISABLED")
        return False
    if DISCORD_ANNOUNCE_REVIEWS == ANNOUNCE_LOGGED_IN and not review.user:
        record("# DISCORD ANNOUNCEMENTS ARE CURRENTLY DISABLED FOR GUESTS")
        return False

    if env != "PROD":
        record("# DISCORD ANNOUNCEMENT SUPPRESSED DUE TO NON-PROD ENVIRONMENT")
        return False

    preview_url = HOST + "static/" + urllib.parse.quote(
         review.zfile.preview_url()
    )

    if mode == "Create":
        discord_post = (
            "*New feedback for {} has been posted!*\n"
            "**{}** written by {}\n"
            "Read: https://museumofzzt.com{}#rev-{}\n"
        )
    else:
        discord_post = (
        "*Feedback for {} has been updated!*\n"
        "**{}** written by {}\n"
        "Read: https://museumofzzt.com{}#rev-{}\n"
    )

    discord_post = discord_post.format(
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


def discord_announce_upload(upload, zfile, env=None):
    if upload.announced:
        return False

    if env is None:
        env = ENV

    if DISCORD_ANNOUNCE_UPLOADS == ANNOUNCE_NONE:
        record("# DISCORD ANNOUNCEMENTS ARE CURRENTLY DISABLED")
        return False
    if DISCORD_ANNOUNCE_UPLOADS == ANNOUNCE_LOGGED_IN and not upload.user:
        record("# DISCORD ANNOUNCEMENTS ARE CURRENTLY DISABLED FOR GUESTS")
        return False

    if env != "PROD":
        record("# DISCORD ANNOUNCEMENT SUPPRESSED DUE TO NON-PROD ENVIRONMENT")
        upload.announced = True
        upload.save()
        return False

    # Check that this isn't an immediate reupload
    if zfile.title == cache.get("DISCORD_LAST_ANNOUNCED_FILE_NAME", ""):
        record("# DISCORD ANNOUNCEMENT SUPPRESSED DUE TO BEING A REPEATED UPLOAD")
        upload.announced = True
        upload.save()
        return False
    else:
        cache.set("DISCORD_LAST_ANNOUNCED_FILE_NAME", zfile.title)

    preview_url = HOST + "static/" + urllib.parse.quote(zfile.preview_url())

    if zfile.release_date:
        year = " ({})".format(str(zfile.release_date)[:4])
    else:
        year = ""
    discord_post = (
        "*A new item has been uploaded to the Museum queue!*\n"
        "**{}** by {}{}\n"
        "Explore: https://museumofzzt.com{}\n"
    ).format(zfile.title, ", ".join(zfile.related_list("authors")), year, urllib.parse.quote(zfile.get_absolute_url()))

    discord_data = {"content": discord_post, "embeds": [{"image": {"url": preview_url}}] }
    resp = requests.post(NEW_UPLOAD_WEBHOOK_URL, headers={"Content-Type": "application/json"}, data=json.dumps(discord_data))

    upload.announced = True
    upload.save()
    return True
