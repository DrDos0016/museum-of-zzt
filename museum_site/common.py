from django.http import Http404
from django.http import HttpResponse
from django.http import QueryDict
from django.template import RequestContext
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django.shortcuts import redirect, get_object_or_404
from django.db import connection
from django.db.models import Count, Avg, Sum, Q
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.urls import reverse

from museum_site.models import *
from museum_site.constants import *
from museum_site.private import NEW_UPLOAD_WEBHOOK_URL, NEW_REVIEW_WEBHOOK_URL, BANNED_IPS

from datetime import datetime, date, timezone, timedelta
from io import BytesIO
from random import randint, shuffle, seed
from time import time
import codecs
import glob
import json
import math
import os
import re
import subprocess
import shutil
import sys
import urllib.parse
import zipfile

import requests
from PIL import Image

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


def env_from_host(host):
    if host in ["beta.museumofzzt.com"]:
        return "BETA"
    elif host in ["museumofzzt.com", "www.museumofzzt.com"]:
        return "PROD"
    else:
        return "DEV"


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


def record(*args, **kwargs):
    if not os.path.isfile("/var/projects/museum-of-zzt/PROD"):
        print(*args, **kwargs)


def redirect_with_querystring(name, qs, *args, **kwargs):
    url = reverse(name, args=args, kwargs=kwargs)
    if qs:
        url += "?" + qs
    return redirect(url)


def profanity_filter(text):
    PROFANITY = [
        'ergneq', 'snttbg', 'shpx', 'fuvg', 'qnza', 'nff', 'cvff', 'phag', 'avttre', 'ovgpu'
    ]
    output = []
    words = text.split(" ")
    for word in words:
        for p in PROFANITY:
            pword = codecs.encode(p, "rot_13")
            if word.lower().find(pword) != -1:
                replacement = ("✖" * len(pword))
                word = word.lower().replace(pword, replacement)
        output.append(word)

    return " ".join(output)


def explicit_redirect_check(request, pk):
    if int(request.session.get("show_explicit_for", 0)) != pk:
        next_param = urllib.parse.quote(request.get_full_path())
        if not request.session.get("bypass_explicit_content_warnings"):
            return redirect_with_querystring("explicit_warning", "next={}&pk={}".format(next_param, pk))
    return "NO-REDIRECT"


def parse_pld(pld):
    context = {}
    colors = []
    upal_vals = []
    indices = [
        0x00, 0x03, 0x06, 0x09, 0x0C, 0x0F, 0x3C, 0x15,
        0xA8, 0xAB, 0xAE, 0xB1, 0xB4, 0xB7, 0xBA, 0xBD,
    ]

    for i in indices:
        upal_val = (pld[i], pld[i+1], pld[i+2])
        upal_vals.append(upal_val)

    # Create swatch
    x = 0
    y = 0
    im = Image.new("RGBA", (256, 16))
    for v in upal_vals:
        colors.append(upal_to_rgb(v))

    context["table_rows"] = [
        {"css_bg": "ega-black-bg", "color": "Black", "custom": colors[0],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[0][2]))[2:]).upper()},
        {"css_bg": "ega-darkblue-bg", "color": "Dark Blue", "custom": colors[1],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[1][2]))[2:]).upper()},
        {"css_bg": "ega-darkgreen-bg", "color": "Dark Green", "custom": colors[2],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[2][2]))[2:]).upper()},
        {"css_bg": "ega-darkcyan-bg", "color": "Dark Cyan", "custom": colors[3],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[3][2]))[2:]).upper()},
        {"css_bg": "ega-darkred-bg", "color": "Dark Red", "custom": colors[4],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[4][2]))[2:]).upper()},
        {"css_bg": "ega-darkpurple-bg", "color": "Dark Purple", "custom": colors[5],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[5][2]))[2:]).upper()},
        {"css_bg": "ega-darkyellow-bg", "color": "Dark Yellow", "custom": colors[6],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[6][2]))[2:]).upper()},
        {"css_bg": "ega-gray-bg", "color": "Gray", "custom": colors[7],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[7][2]))[2:]).upper()},
        {"css_bg": "ega-darkgray-bg", "color": "Dark Gray", "custom": colors[8],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[8][2]))[2:]).upper()},
        {"css_bg": "ega-blue-bg", "color": "Blue", "custom": colors[9],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[9][2]))[2:]).upper()},
        {"css_bg": "ega-green-bg", "color": "Green", "custom": colors[10],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[10][2]))[2:]).upper()},
        {"css_bg": "ega-cyan-bg", "color": "Cyan", "custom": colors[11],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[11][2]))[2:]).upper()},
        {"css_bg": "ega-red-bg", "color": "Red", "custom": colors[12],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[12][2]))[2:]).upper()},
        {"css_bg": "ega-purple-bg", "color": "Purple", "custom": colors[13],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[13][2]))[2:]).upper()},
        {"css_bg": "ega-yellow-bg", "color": "Yellow", "custom": colors[14],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[14][2]))[2:]).upper()},
        {"css_bg": "ega-white-bg", "color": "White", "custom": colors[15],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[15][2]))[2:]).upper()},
    ]

    return render_to_string("museum_site/blocks/fv-palette.html", context)


def upal_to_rgb(v):
    (r_comp, g_comp, b_comp) = (v[0], v[1], v[2])

    r_intensity = r_comp / 63
    g_intensity = g_comp / 63
    b_intensity = b_comp / 63

    r = int(r_intensity * 255)
    g = int(g_intensity * 255)
    b = int(b_intensity * 255)

    return (r, g, b)


def banned_ip(ip):
    if ip in BANNED_IPS:
        return True
    elif "." in ip:
        ip = ".".join(ip.split(".")[:-1]) + ".*"
        if ip in BANNED_IPS:
            return True
        return False
