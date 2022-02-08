from django import VERSION
from django.http import Http404
from django.http import HttpResponse
from django.http import QueryDict
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.shortcuts import redirect, get_object_or_404
from django.db import connection
from django.db.models import Count, Avg, Sum, Q
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
# from django.utils.timezone import utc
# from django.contrib.auth import logout, authenticate, login as auth_login


from museum_site.models import *
from museum_site.constants import *
from .private import NEW_UPLOAD_WEBHOOK_URL, NEW_REVIEW_WEBHOOK_URL

from datetime import datetime, timezone, timedelta
from io import BytesIO
from random import randint, shuffle, seed
from time import time
import glob
import json
import math
import os
import re
import subprocess
import sys
import urllib.parse
import zipfile

import requests
from PIL import Image

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_PATH = os.path.join(SITE_ROOT, "temp")
BASE_PATH = os.path.join(SITE_ROOT, "museum_site", "static", "data", "base")
STATIC_PATH = os.path.join(SITE_ROOT, "museum_site", "static")
CSS_INCLUDES = [
    "grid.css", "zzt.css", "low-res.css", "forms.css", "model-blocks.css"
]
TRACKING = True  # Analytics
DEBUG = True if os.path.isfile("/var/projects/DEV") else False
PAGE_SIZE = 25
PAGE_LINKS_DISPLAYED = 30
LIST_PAGE_SIZE = 250
UPLOADS_ENABLED = True
UPLOAD_CAP = 1048576  # 1 Megabyte
YEAR = datetime.now().year
PYTHON_VERSION = sys.version
DJANGO_VERSION = VERSION
START_TIME = datetime.utcnow()
BOOT_TS = START_TIME.strftime("%m%d%H%M%S")

FILE_VIEWER_TEXT_EXTENSIONS = (
    "", ".135", ".135.asc", ".1st", ".ans", ".asm", ".bas", ".bat", ".bb",
    ".bi", ".bin", ".c", ".cc", ".cfg", ".chr", ".cpp", ".crd", ".dat", ".def",
    ".deu", ".diz", ".doc", ".ds_store", ".e", ".eed", ".eng", ".err", ".ex",
    ".faq", ".frm", ".fyi", ".gitignore", ".gud", ".h", ".hlp", ".inc", ".inf",
    ".ini", ".java", ".json", ".log", ".lst", ".lua", ".mac", ".map", ".md",
    ".me", ".msg", ".muz", ".new", ".nfo", ".now", ".olf", ".pas", ".py",
    ".reg", ".rtf", ".sdi", ".sh", ".slv", ".sol", ".st", ".theme", ".txt",
    ".wps", ".wri", ".zln", ".zml", ".zzl", ".zzm",
)

FILE_VIEWER_HEX_EXTENSIONS = (
    ".hi", ".zzt", ".brd", ".mh", ".sav", ".szt", ".mwz", ".z_t", ".hgs",
)

FILE_VIEWER_B64_EXTENSIONS = (
    ".jpg", ".jpeg", ".bmp", ".gif", ".png", ".ico", ".avi"
)

FILE_VIEWER_AUDIO_EXTENSIONS = (
    ".wav", ".mp3", ".ogg", ".mid", ".midi"
)

EMAIL_ADDRESS = "doctordos@gmail.com"


GENRE_LIST = (
    "24HoZZT", "Action", "Adventure", "Advertisement", "Arcade", "Art",
    "Beta", "BKZZT", "Bugfix", "Cameo", "Catalog", "Cinema", "Comedy", "Comic",
    "Compilation", "Contest", "Demo", "Dungeon", "Edutainment", "Engine",
    "Experimental", "Fangame", "Fantasy", "Fighting", "Font",
    "Help", "Horror", "Incomplete", "Ludum Dare", "Magazine", "Maze",
    "Minigame", "Mod", "Multiplayer", "Music", "Mystery",
    "Official", "Other", "Parody", "Platformer", "Puzzle", "Racing", "Random",
    "Remake", "Registered", "Retro", "RPG", "Sci-Fi", "Shareware",
    "Shooter", "Simulation", "Space", "Sports", "Story", "Strategy", "Toolkit",
    "Trippy", "Trivia", "Update", "Utility", "WoZZT"
)

SORT_CODES = {
    "title": ["sort_title"],
    "author": ["author", "sort_title"],
    "company": ["company", "sort_title"],
    "id": ["-id"],
    "rating": ["-rating", "sort_title"],
    "release": ["release_date", "sort_title"],
    "-release": ["-release_date", "sort_title"],
    "published": ["-publish_date", "-id"],
    "roulette": ["?"],
    "uploaded": ["-id"],
}

PLAY_METHODS = {
    "archive": {"name": "Archive.org - DosBox Embed"},
    "zeta": {"name": "Zeta"},
}


def populate_collection_params(data):
    params = "?"
    keys = [
        "mode", "rng_seed", "author", "year", "genre", "company", "letter",
        "page", "sort"
    ]
    for k in keys:
        if data.get(k):
            params += k + "=" + str(data[k]) + "&"
    params = params[:-1]
    return params


def qs_sans(params, key):
    """ Returns a query string with a key removed """
    qs = params.copy()

    # If key is actually a list
    if isinstance(key, list):
        qs_nokey = qs.copy()
        for k in key:
            if k in qs:
                qs_nokey.pop(k)
    else:
        if key in qs:
            qs_nokey = qs.copy()
            qs_nokey.pop(key)
        else:
            qs_nokey = qs

    return qs_nokey.urlencode()


def serve_file(file_path="", named=""):
    """ Returns an HTTPResponse containing the given file with an optional
        name
    """
    if not named:
        named = os.path.basename(file_path)

    if not os.path.isfile(file_path):
        raise Http404("Source file not found")

    response = HttpResponse(content_type="application/octet-stream")
    response["Content-Disposition"] = "attachment; filename={}".format(named)
    with open(file_path, "rb") as fh:
        response.write(fh.read())
    return response


def slash_separated_sort(orig):
    temp_list = orig.split("/")
    temp_list.sort()
    output = "/".join(temp_list)
    return output


def env_from_host(host):
    if host in ["beta.museumofzzt.com"]:
        return "BETA"
    elif host in ["museumofzzt.com"]:
        return "PROD"
    else:
        return "DEV"


def set_captcha_seed(request):
    request.session["captcha-seed"] = (
        str(datetime.now()).replace(
            "-", ""
        ).replace(
            ":", ""
        ).replace(
            ".", ""
        ).replace(
            " ", ""
        )
    )


# Decorators
def dev_only(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) != "DEV":
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner


def non_production(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) not in ["DEV", "BETA"]:
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner


def prod_only(func, *args, **kwargs):
    def inner(*args, **kwargs):
        request = kwargs.get("request", args[0])

        # Check host
        host = request.get_host()
        if env_from_host(host) != "PROD":
            raise Http404
        else:
            return func(*args, **kwargs)
    return inner


def get_selected_view_format(
    request,
    available_views=["detailed", "list", "gallery"]
):
    # GET > Session > Default
    view = None
    if request.GET.get("view"):
        view = request.GET["view"]
    elif request.session.get("view"):
        view = request.session["view"]
    if view not in available_views:  # Default
        view = "detailed"
    request.session["view"] = view
    return view


def get_page_size(view):
    page_sizes = {
        "detailed": PAGE_SIZE,
        "list": LIST_PAGE_SIZE,
        "gallery": PAGE_SIZE,
    }
    return page_sizes.get(view, PAGE_SIZE)


def get_pagination_data(request, data, qs):
    data["page_number"] = int(request.GET.get("page", 1))
    data["paginator"] = Paginator(qs, get_page_size(data["view"]))
    data["page"] = data["paginator"].get_page(data["page_number"])

    # Bounds checking
    if data["page_number"] < 1:
        data["page_number"] = 1
    elif data["page_number"] > data["paginator"].num_pages:
        data["page_number"] = data["paginator"].num_pages

    # Determine lowest and highest visible page
    lower = max(1, data["page_number"] - (PAGE_LINKS_DISPLAYED // 2))
    upper = lower + PAGE_LINKS_DISPLAYED

    # Don't display too many pages
    if upper > data["paginator"].num_pages + 1:
        upper = data["paginator"].num_pages + 1

    data["page_range"] = range(lower, upper)
    return data


def throttle_check(
    request, attempt_name, expiration_name, max_attempts,
    lockout_mins=5
):
    # Origin time for calculating lockout
    now = datetime.now()

    # Increment attempts
    request.session[attempt_name] = request.session.get(attempt_name, 0) + 1

    # Lockout after <max_attempts>
    if request.session[attempt_name] > max_attempts:
        # If they're already locked out and the timer's expired, resume
        if (
            request.session.get(expiration_name) and
            (str(now)[:19] > request.session[expiration_name])
        ):
            request.session[attempt_name] = 1
            del request.session[attempt_name]
            del request.session[expiration_name]
            return True

        # Otherwise lock them out
        delta = timedelta(minutes=lockout_mins)
        request.session[expiration_name] = str(now + delta)
        return False
    return True


def get_max_upload_size(request):
    max_upload_size = UPLOAD_CAP
    if request.user.is_authenticated:
        max_upload_size = request.user.profile.max_upload_size
    return max_upload_size


def zipinfo_datetime_tuple_to_str(raw):
    dt = raw.date_time
    y = str(dt[0])
    m = str(dt[1]).zfill(2)
    d = str(dt[2]).zfill(2)
    h = str(dt[3]).zfill(2)
    mi = str(dt[4]).zfill(2)
    s = str(dt[5]).zfill(2)
    out = "{}-{}-{} {}:{}:{}".format(y, m, d, h, mi, s)
    return out


def discord_announce_review(review, env=None):
    if env is None:
        env = ENV

    if env != "PROD":
        print("# DISCORD ANNOUNCEMENT SUPPRESSED DUE TO NON-PROD ENVIRONMENT")
        return False

    preview_url = HOST + "static/" + urllib.parse.quote(
         review.file.screenshot_url()
    )

    discord_post = (
        "*A new review for {} has been posted!*\n"
        "**{}** written by {}\n"
        "Read: https://museumofzzt.com{}#rev-{}\n"
    ).format(
        review.file.title, review.title, review.get_author(),
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
        print("# DISCORD ANNOUNCEMENT SUPPRESSED DUE TO NON-PROD ENVIRONMENT")
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


def any_plus(choices):
    """ Appends Any as an option to the choices for a form"""
    choices = list(choices)
    choices.insert(0, ("any", "- Any -"))
    return choices


def optimize_image(image):
    if os.path.isfile(image):
        status = os.system("optipng -o7 -strip=all -fix -nc -quiet " + image)
        if status == 0:
            return True
    return False


def move_uploaded_file(upload_directory, uploaded_file, custom_name=""):
    upload_filename = (
        custom_name if custom_name else uploaded_file.name
    )
    file_path = os.path.join(STATIC_PATH, upload_directory, upload_filename)
    with open(file_path, 'wb+') as fh:
        for chunk in uploaded_file.chunks():
            fh.write(chunk)

    return file_path


def crop_file(file_path, size=(480, 350)):
    image = Image.open(file_path)
    image = image.crop((0, 0, size[0], size[1]))
    image.save(file_path)
    optimize_image(file_path)
    return True


def get_detail_suggestions(file_list):
    suggestions = {
        "hints": [],
        "hint_ids": [],
        "unknown_extensions": [],
    }
    for name in file_list:
        ext = os.path.splitext(os.path.basename(name).upper())
        if ext[1] == "":
            ext = ext[0]
        else:
            ext = ext[1]

        if ext in EXTENSION_HINTS:
            suggest = (EXTENSION_HINTS[ext][1])
            suggestions["hints"].append(
                (name, EXTENSION_HINTS[ext][0], suggest)
            )
            suggestions["hint_ids"] += EXTENSION_HINTS[ext][1]
        elif ext == "":  # Folders hit this
            continue
        else:
            suggestions["unknown_extensions"].append(ext)

    suggestions["hint_ids"] = set(suggestions["hint_ids"])
    suggestions["unknown_extensions"] = set(suggestions["unknown_extensions"])
    return suggestions

def epoch_to_unknown(calendar_date):
    if calendar_date.year <= 1970:
        return "Unknown"
    return calendar_date
