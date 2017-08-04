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

from museum_site.models import *
from datetime import datetime
from random import randint
import math
import zipfile
import glob
import os
import subprocess
import sys

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKING = True  # Analytics
DEBUG = True if os.path.isfile("/var/projects/DEV") else False
PAGE_SIZE = 25
LIST_PAGE_SIZE = 300
UPLOADS_ENABLED = True
UPLOAD_CAP = 1048576  # 1 Megabyte
YEAR = datetime.now().year
PYTHON_VERSION = sys.version
DJANGO_VERSION = VERSION

EMAIL_ADDRESS = "doctordos@gmail.com"

print("MUSEUM OF ZZT STARTUP")
print(str(datetime.utcnow()))
print("Python:", PYTHON_VERSION)
print("Django:", DJANGO_VERSION)

"""
CATEGORY_LIST = (
    ("ZZT", "ZZT World"),
    ("ZZM", "ZZM Soundtrack"),
    ("ZIG", "ZIG World"),
    ("Utility", "External Utility"),
    ("SZZT", "Super ZZT World"),
    ("Etc", "Etc."),
)
"""

CHARSET_LIST = (
    ("cp437.png", "Code Page 437 -- RECOMMENDED"),
)

CUSTOM_CHARSET_LIST = (
    "0003-1012.png",
    "2256-24HOZZTH.png",
    "0042-AKFONT.png",
    "1683-AMB.png",
    "1826-ART.png",
    "0097-BE2FONT.png",
    "1414-Black.png",
    "0133-bobt.png",
    "0085-BQUEST.png",
    "0421-Bren.png",
    "1690-CCFONT.png",
    "0593-CHUNKY.png",
    "1683-CHUNKY.png",
    "1683-COM_DEMO.png",
    "1975-COMMFONT.png",
    "0325-CRAZY.png",
    "0758-CRAZY.png",
    "0610-DARK2.png",
    "0999-DEATHII2.png",
    "2116-DIGFONT.png",
    "0303-Dino.png",
    "0314-DM1.png",
    "0352-dragon.png",
    "0511-Dzzt.png",
    "0365-EFZI.png",
    "0392-EFZI.png",
    "0382-era.png",
    "0017-Ermhey.png",
    "0145-Ermhey.png",
    "0191-Ermhey.png",
    "0674-Ermhey.png",
    "1344-Ermhey.png",
    "1670-ERMHEY.png",
    "1683-F0.png",
    "2172-F0.png",
    "0268-FONT3D.png",
    "0459-FUNTOWN.png",
    "2186-GEO2.png",
    "0525-HOFONT.png",
    "0325-HOFONT.png",
    "1683-JULIE.png",
    "1683-JULIE2.png",
    "0624-Kevin.png",
    "0625-KEWL.png",
    "0626-Kewlio.png",
    "1683-KING.png",
    "1683-KOOL.png",
    "1845-KRACKEN.png",
    "2146-KURIE.png",
    "0689-lr9.png",
    "0709-MARIORPG.png",
    "0776-Merlin.png",
    "0799-NEW.png",
    "0801-OCELOT.png",
    "0848-PACMAN.png",
    "0859-PASPLATT.png",
    "0878-Pokemon.png",
    "1683-POOTER.png",
    "1683-POOTER2.png",
    "1135-QUEST.png",
    "1245-QUEST.png",
    "0940-QUEST3D.png",
    "0906-Question.png"
    "1115-Question.png",
    "0950-RAT-RACE.png",
    "1282-RED.png",
    "0688-REFRITOS.png",
    "0966-REFRITOS.png",
    "1263-RPG.png",
    "1127-SAILOROO.png",
    "1051-SHAKE.png",
    "1124-SQUBE.png",
    "1033-SSCA.png",
    "1034-SSCA.png",
    "1135-Ssca2.png",
    "1137-SSG.png",
    "0601-STARWAR.png",
    "1142-Starwar.png",
    "1189-Teatime.png",
    "1190-Teatime2.png",
    "1882-TREXBOYF.png",
    "0188-TWFONT.png",
    "1227-TWFONT.png",
    "0253-VAMPIRE.png",
    "1284-VILLAGE.png",
    "1285-VILLAGE2.png",
    "1760-VILLAGE2.png",
    "1315-WIETH.png",
    "1853-WISHFONT.png",
    "1360-YUMMY.png",
    "1361-YVS2FONT.png",
    "1627-ZBERT.png",
    "1861-ZEPHFONT.png",
    "1880-ZEPHFONT.png",
    "0533-ZFONT.png",
    "2323-ZFONT2.png",
    "1826-ZXS02.png",
    "1826-ZXSMAIN.png",
    "1387-Zyth.png",
    "1387-Zythtxt.png",
    "1703-ZZFACES.png",
    "1682-ZZFont.png",
    "2298-ZZFONT.png",
    "1057-ZZTRINGA.png",
    "2323-ZFONT2.png",
    "2349-ZFONT2.png",
    "2359-ZZFACES.png",
)

DETAIL_LIST = (
    "Contest"
    "Etc."
    "Featured Game"
    "Modified Graphics"
    "Linux Compatible Program"
    "Modified Executable"
    "MS-DOS Compatible Program"
    "OSX Compatible"
    "Super ZZT World"
    "Utility"
    "Windows 16-bit"
    "Windows 32-bit"
    "Windows 64-bit"
    "ZZT World"
    "ZZM Audio"
    "ZIG World"
)

GENRE_LIST = (
    "24HoZZT",
    "Action", "Adventure", "Arcade", "Art", "Beta", "BKZZT",
    "Cameo", "Catalog", "Cinema", "Comedy", "Comic",
    "Compilation", "Contest", "Demo",
    "Dungeon", "Edutainment", "Engine", "Experimental", "Explicit", "Fantasy",
    "Fighting", "Font", "Help", "Horror", "Incomplete", "Ludum Dare",
    "Magazine", "Maze", "Minigame", "Multiplayer", "Music", "Mystery",
    "Non-English", "Official", "Other",
    "Parody", "Platformer", "Puzzle", "Racing",
    "Random", "Remake", "Registered", "Retro", "RPG", "Sci-Fi", "Shareware",
    "Shooter", "Simulation", "Space",
    "Sports", "Story", "Strategy", "Toolkit",
    "Trippy", "Trivia", "Tutorial",
    "Update", "Utility", "WoZZT"
)

SORT_CODES = {
    "title": ["sort_title"],
    "author": ["author", "sort_title"],
    "company": ["company", "sort_title"],
    "rating": ["-rating", "sort_title"],
    "release": ["release_date", "sort_title"]
}

ADV_SEARCH_DEFAULTS = [
    str(DETAIL_ZZT),
    str(DETAIL_SZZT),
    str(DETAIL_UTILITY),
]


def qs_sans(params, key):
    """ Returns a query string with a key removed """
    qs = params.copy()

    if key in qs:
        qs_nokey = qs.copy()
        qs_nokey.pop(key)
    else:
        qs_nokey = qs

    return qs_nokey.urlencode()
