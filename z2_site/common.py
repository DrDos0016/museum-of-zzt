# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django import VERSION
from django.http import Http404
from django.http import HttpResponse
from django.http import QueryDict
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db import connection
from django.db.models import Count, Avg, Sum, Q
from django.core.exceptions import ValidationError
# from django.utils.timezone import utc
# from django.contrib.auth import logout, authenticate, login as auth_login

from z2_site.models import *
from datetime import datetime
from random import randint
import math
import zipfile
import glob
import os
import sys

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKING = True  # Analytics
DEBUG = True if os.path.isfile("/var/projects/DEV") else False
PAGE_SIZE = 25
LIST_PAGE_SIZE = 150
UPLOAD_CAP = 1048576  # 1 Megabyte
YEAR = datetime.now().year
PYTHON_VERSION = sys.version
DJANGO_VERSION = VERSION

print("Python:", PYTHON_VERSION)
print("Django:", DJANGO_VERSION)

CHARSET_LIST = (
    ("cp437", "Code Page 437 -- RECOMMENDED"),
)

# Format -- Filename, display name, auto load
CUSTOM_CHARSET_LIST = (
    "1012",
    "black",
    "bobt",
    "bren",
    "ccfont",
    "chunky",
    "commfont",
    "crazy",
    "dark2",
    "deathii2",
    "digfont",
    "dino",
    "dragon",
    "dzzt",
    "efzi",
    "ermhey",
    "hofont",
    "kevin",
    "kracken",
    "lr9",
    "mariorpg",
    "new",
    "pacman",
    "question",
    "quest",
    "red",
    "sqube",
    "ssca2",
    "ssca",
    "ssg",
    "trexboyf",
    "twfont",
    "vampire",
    "village2",
    "wieth",
    "wishfont",
    "zbert",
    "zephfont",
    "zyth",
    "zythtxt",
    "zzfaces",
    "zztringa",
)

DETAIL_LIST = (
    "MS-DOS", "Windows 16-bit", "Windows 32-bit", "Windows 64-bit", "Linux",
    "OSX", "Featured", "Contest", "Soundtrack", "Font", "Hack"
)

GENRE_LIST = (
    "Action", "Adventure", "Alternative", "Arcade", "Art", "Cameo",
    "Catalog", "Cinema", "Comedy", "Compilation", "Demo",
    "Dungeon", "Edutainment", "Engine", "Erotic", "Fantasy",
    "Help", "Horror", "Incomplete", "Magazine", "Maze",
    "Minigame", "Multiplayer", "Music", "Mystery", "Other",
    "Parody", "Philosophy", "Platformer", "Puzzle", "Racing",
    "Random", "Remake", "RPG", "Sci-Fi", "Shooter", "Simulation",
    "Sports", "Strategy", "Toolkit", "Trippy", "Trivia", "Tutorial"
)


def qs_sans(params, key):
    """ Returns a query string with a key removed """
    qs = params.copy()

    if key in qs:
        qs_nokey = qs.copy()
        qs_nokey.pop(key)
    else:
        qs_nokey = qs

    print(qs_nokey.urlencode())
    return qs_nokey.urlencode()
