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
from museum_site.queries import *
from datetime import datetime
from io import BytesIO
from random import randint, shuffle, seed
from time import time
import glob
import math
import os
import re
import subprocess
import sys
import urllib.parse
import zipfile

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMP_PATH = os.path.join(SITE_ROOT, "tmp")
BASE_PATH = os.path.join(SITE_ROOT, "museum_site", "static", "data", "base")
STATIC_PATH =  os.path.join(SITE_ROOT, "museum_site", "static")
CSS_INCLUDES = ["grid.css", "responsive.css", "zzt.css"]
TRACKING = True  # Analytics
DEBUG = True if os.path.isfile("/var/projects/DEV") else False
PAGE_SIZE = 25
LIST_PAGE_SIZE = 300
UPLOADS_ENABLED = True
UPLOAD_CAP = 1048576  # 1 Megabyte
YEAR = datetime.now().year
PYTHON_VERSION = sys.version
DJANGO_VERSION = VERSION
START_TIME = datetime.utcnow()
BOOT_TS = START_TIME.strftime("%m%d%H%M%S")
ARCHIVE_COLLECTION = "open_source_software" if not DEBUG else "test_collection"

if os.path.isfile(os.path.join(SITE_ROOT, "ia.cfg")):
    with open(os.path.join(SITE_ROOT, "ia.cfg")) as fh:
        IA_SUPPORT = True
        IA_ACCESS = fh.readline().strip()
        IA_SECRET = fh.readline().strip()
else:
    IA_SUPPORT = False
    IA_ACCESS = None
    IA_SECRET = None

EMAIL_ADDRESS = "doctordos@gmail.com"

print("MUSEUM OF ZZT STARTUP")
print(START_TIME)
print("Site Root:", SITE_ROOT)
print("Python:", PYTHON_VERSION)
print("Django:", DJANGO_VERSION)

LETTERS = (
    "1", "a", "b", "c", "d", "e", "f", "g", "h",
    "i", "j", "k", "l", "m", "n", "o", "p", "q",
    "r", "s", "t", "u", "v", "w", "x", "y", "z"
)

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
    "2613-ZELDA3.png",
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

CUSTOM_CHARSET_MAP = {}
for charset_name in CUSTOM_CHARSET_LIST:
    try:
        CUSTOM_CHARSET_MAP[int(charset_name.split('-', 1)[0])] = charset_name
    except ValueError:
        pass

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
    "Action", "Adventure", "Advertisement", "Arcade", "Art", "Beta", "BKZZT",
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
    "id": ["-id"],
    "rating": ["-rating", "sort_title"],
    "release": ["release_date", "sort_title"],
    "published": ["-publish_date", "-id"],
    "roulette": ["?"]
}

ADV_SEARCH_DEFAULTS = [
    str(DETAIL_ZZT),
    str(DETAIL_SZZT),
    str(DETAIL_UTILITY),
]

PACKAGE_PROFILES = (
    {
        "name": "ZZT v3.2 Registered",
        "directory": "ZZT32-REG",
        "use_cfg": True,
        "registered": True,
        "prefix": "zzt_",
        "executable": "ZZT.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine.",
    },
    {
        "name": "Super ZZT Registered",
        "directory": "SZZT-REG",
        "use_cfg": False,
        "registered": True,
        "prefix": "superzzt_",
        "executable": "SUPERZ.EXE",
        "engine": "Super ZZT",
        "auto_desc": "World created using the Super ZZT engine.",
    },
    {
        "name": "CleanZZT",
        "directory": "CLEANZZT",
        "use_cfg": True,
        "registered": True,
        "prefix": "cleanzzt_",
        "executable": "CLEANZZT.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under Clean ZZT, a customized ZZT executable that removes certain default sound effects and messages",
    },
    {
        "name": "Super ZZT v4.0",
        "directory": "SZZT40",
        "use_cfg": False,
        "registered": True,
        "prefix": "superzzt40_",
        "executable": "s.bat",
        "engine": "Super ZZT",
        "auto_desc": "World created using the Super ZZT engine, and running under Super ZZT 4.0, a customized Super ZZT executable to increase certain memory limitations",
    },
    {
        "name": "ZZT v2.0 Shareware",
        "directory": "ZZT20-SW",
        "use_cfg": True,
        "registered": False,
        "prefix": "zzt20sw_",
        "executable": "ZZT.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 2.0 Shareware edition.",
    },
    {
        "name": "ZZT v3.1 Shareware",
        "directory": "ZZT31-SW",
        "use_cfg": True,
        "registered": False,
        "prefix": "zzt31sw_",
        "executable": "ZZT.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 3.1 Shareware edition.",
    },
    {
        "name": "ZZT v3.2 Shareware",
        "directory": "ZZT32-SW",
        "use_cfg": True,
        "registered": False,
        "prefix": "zztsw_",
        "executable": "ZZT.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 3.2 Shareware edition.",
    },
    {
        "name": "ZZT v4.0",
        "directory": "ZZT40",
        "use_cfg": True,
        "registered": True,
        "prefix": "zzt40_",
        "executable": "zzt.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 4.0, a customized ZZT executable to increase certain memory limitations and fix bugs with the original program.",
    },
    {
        "name": "ZZT v4.0 - No MSG",
        "directory": "ZZT40",
        "use_cfg": True,
        "registered": True,
        "prefix": "zzt40nomsg_",
        "executable": "zztnomsg.EXE",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 4.0 No MSG, a customized ZZT executable to increase certain memory limitations, fix bugs with the original program, and remove certain default sounds and messages.",
    },
    {
        "name": "ZZT v4.1",
        "directory": "ZZT41",
        "use_cfg": True,
        "registered": True,
        "prefix": "zzt41_",
        "executable": "zzt41.exe",
        "engine": "ZZT",
        "auto_desc": "World created using the ZZT engine, and running under ZZT 4.1 No MSG, a customized ZZT executable to increase certain memory limitations, fix bugs with the original program, and remove certain default sounds and messages.",
    },
    {
        "name": "ZZT Music Player v2.0",
        "directory": "ZZTMP20",
        "prefix": "zztmp20_",
        "executable": "ZZTMPLAY.EXE",
        "engine": "ZZM",
        "auto_desc": "ZZM files being played using ZZT Music Player v2.0, a program to play ZZM music, a format designed to play ZZT's PC speaker sounds in a more traditional audio player. Note that ZZM files do not sound identical to the same sounds produced in ZZT. (If both formats are available, ZZT is the superior choice for playback accuracy.)",
    }
)

PLAY_METHODS = {
    "archive": {"name":"Archive.org - DosBox Embed"},
    "zeta": {"name":"Zeta"},
}

def populate_collection_params(data):
    params = "?"
    keys = ["mode", "rng_seed", "author", "year", "genre", "company", "letter", "page", "sort"]
    for k in keys:
        if data.get(k):
            params += k + "=" + str(data[k]) + "&"
    params = params[:-1]
    return params



def get_view_format(request):
    """ Returns Detailed/List/Gallery based on selected View type """
    if request.GET.get("view"):
        return request.GET["view"]
    elif request.COOKIES.get("view"):
        return request.COOKIES["view"]
    else:
        return "detailed"


def qs_sans(params, key):
    """ Returns a query string with a key removed """
    qs = params.copy()

    if key in qs:
        qs_nokey = qs.copy()
        qs_nokey.pop(key)
    else:
        qs_nokey = qs

    return qs_nokey.urlencode()


def set_captcha_seed(request):
    request.session["captcha-seed"] = str(datetime.now()).replace("-", "").replace(":", "").replace(".", "").replace(" ", "")
