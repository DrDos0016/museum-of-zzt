import glob
import os

from collections import namedtuple

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Private settings - (Patron Locked Content, IA API)
try:
    from museum_site.private import (
        PASSWORD2DOLLARS, PASSWORD5DOLLARS, IA_ACCESS, IA_SECRET, BANNED_IPS
    )
    IA_SUPPORT = True
except ModuleNotFoundError:
    print("PRIVATE.PY NOT FOUND. USING DEV VALUES")
    PASSWORD2DOLLARS = "test2dollars"
    PASSWORD5DOLLARS = "test5dollars"
    IA_ACCESS = "Not found"
    IA_SECRET = "Not found"
    IA_SUPPORT = False
    BANNED_IPS = [""]

# Accounts
ALLOW_REGISTRATION = True
REQUIRE_CAPTCHA = False
MIN_PASSWORD_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
MAX_REGISTRATION_ATTEMPTS = 3
MAX_PASSWORD_RESETS = 5

TERMS_DATE = "2021-08-01"
TERMS = """
# Museum of ZZT - Terms of Service (v.2021.08.01)

## Your Data
User passwords are stored in a hashed and salted format preventing anyone from
easily acquiring them. Nevertheless using a unique password is strongly
encouraged as the Museum of ZZT and its security are essentially a one person
operation.

On occasion to better facilitate site development the Museum of ZZT's database
is exported, scrubbed, and published to be used as a starting point for
development. The scrubbing process includes data being blanked out or replaced
with dummy data. This includes IP addresses, email addresses, all session data,
password hashes, and profile information.

Because some data is captured in these database dumps it is possible for
deleted information to still be available. When submitting data to the Museum
of ZZT, please consider that there is a possibility that it is never truly
gone forever when erased from the live site.

By accepting these terms of service you are acknowledging the potential for
your data to persist in potentially unforeseen ways, and providing permission
for that data to be stored, shared, and reproduced in Worlds of ZZT projects.

## Email
Your email address (and patron email address) will not be shared with third
parties. A valid email address is required to verify your account and provide
password reset functionality.

By accepting these terms of service you are providing permission to store
this information within the Museum of ZZT's database.

## Patronage
Users will have their account's email address or a specifically chosen Patreon
email address cross-referenced against a nightly generated list of active
Worlds of ZZT patrons. If a match is found your account will be marked as a
patron with the current pledge and selected tier recorded. This information is
used to allow users to access patron exclusive perks based on these values.

At the time of writing, accounts which no longer remain patrons either due to
denied payments or canceled pledges will not automatically lose their patron
status.

By accepting these terms of service you are providing permission to link your
Museum of ZZT account to Worlds of ZZT Patreon information and storing relevant
data about your patronage to provide access to patron exclusive content and
site functionality.

## User Conduct

It is a goal of the Worlds of ZZT project to help create and foster a ZZT
community which is welcoming and inclusive to all regardless of age, race,
gender, ZZT experience, religion, orientation, etc. Users and guests
contributing to this community are expected to do so in a way which aligns with
this goal.

Do not abuse functionality to alter your username. Impersonating other users or
using characters to adversely affect (successfully or otherwise) page rendering
are strictly forbidden.

Users are expected to abide by all Museum rules and policies when uploading
files, posting reviews, and leaving comments.

Users are expected to be respectful of other community members and privately
contact staff when there is an issue either through direct messages on Discord
or via email.

By accepting these terms of service you are agreeing to conduct yourself in a
manner that aligns with these ideals.

## Violations

Violations of these terms may result in you and/or your account having
permissions to participate in certain site functions (including but not limited
to uploading files, posting reviews, participating on the Worlds of ZZT
Discord) being revoked for any amount of time felt necessary.

By accepting these terms of service you are acknowledging and agreeing to the
consequences of violating these terms.
"""
TOKEN_EXPIRATION_SECS = 600

# Admin information
ADMIN_NAME = "Dr. Dos"

# Host/Environment information
if os.path.isfile(os.path.join(SITE_ROOT, "PROD")):
    HOST = "https://museumofzzt.com/"
    PROTOCOL = "https"
    DOMAIN = "museumofzzt.com"
    ENV = "PROD"
elif os.path.isfile(os.path.join(SITE_ROOT, "DEV")):
    HOST = "http://django.pi:8000/"
    PROTOCOL = "http"
    DOMAIN = "django.pi:8000"
    ENV = "DEV"
elif os.path.isfile(os.path.join(SITE_ROOT, "BETA")):
    HOST = "https://beta.museumofzzt.com/"
    PROTOCOL = "https"
    DOMAIN = "beta.museumofzzt.com"
    ENV = "BETA"

# Magic Numbers
UPCOMING_ARTICLE_MINIMUM_PATRONAGE = 200
UNPUBLISHED_ARTICLE_MINIMUM_PATRONAGE = 500
NO_PAGINATION = 9999

# File details
DETAIL_DOS = 1
DETAIL_WIN16 = 2
DETAIL_WIN32 = 3
DETAIL_WIN64 = 4
DETAIL_LINUX = 5
DETAIL_OSX = 6
DETAIL_FEATURED = 7
DETAIL_ZZM = 9
DETAIL_GFX = 10
DETAIL_MOD = 11
DETAIL_SZZT = 13
DETAIL_UTILITY = 14
DETAIL_ZZT = 15
DETAIL_ZIG = 16
DETAIL_LOST = 17
DETAIL_UPLOADED = 18
DETAIL_REMOVED = 19
DETAIL_CORRUPT = 20
DETAIL_ZZT_BOARD = 21
DETAIL_ZZT_SAVE = 22
DETAIL_SZZT_BOARD = 23
DETAIL_SZZT_SAVE = 24
DETAIL_ZZT_SCORE = 25
DETAIL_SZZT_SCORE = 26
DETAIL_CLONE_WORLD = 27  # NEW
DETAIL_SOURCE_CODE = 28
DETAIL_TEXT = 29
DETAIL_HTML = 30
DETAIL_IMAGE = 31
DETAIL_VIDEO = 32
DETAIL_PROGRAM = 33
DETAIL_COMPRESSED = 34
DETAIL_ROM = 35
DETAIL_AUDIO = 36
DETAIL_WEAVE = 37

# Front Page
FP = namedtuple(
    "FrontPageItems",
    ["ARTICLES_SHOWN", "NEW_RELEASES_SHOWN", "FILES_SHOWN", "REVIEWS_SHOWN"],
)(
    ARTICLES_SHOWN=10,
    NEW_RELEASES_SHOWN=12,
    FILES_SHOWN=12,
    REVIEWS_SHOWN=10
)

# Character Sets
CHARSETS = [
    {
        "id": 0,
        "filename": "cp437.png",
        "name": "Code Page 437",
        "engine": "ZZT",
    },
    {
        "id": 0,
        "filename": "szzt-cp437.png",
        "name": "Code Page 437 (SZZT)",
        "engine": "SZZT",
    }
]
CUSTOM_CHARSETS = []

# Paths
DATA_PATH = os.path.join(SITE_ROOT, "museum_site", "static", "data") + os.sep
CHARSET_PATH = os.path.join(
    SITE_ROOT, "museum_site", "static", "images", "charsets"
) + os.sep

pngs = sorted(glob.glob(
    os.path.join(
        SITE_ROOT, "museum_site", "static", "images", "charsets", "*.png"
    )
))
for png in pngs:
    filename = os.path.basename(png)
    if filename.find("cp437") != -1:  # Skip non-custom fonts
        continue

    if filename.startswith("szzt"):
        charset_id = int(filename.split("-")[1])
    else:
        charset_id = int(filename.split("-")[0])

    name = filename.split("-")[-1][:-4]
    engine = "ZZT" if "szzt" not in filename else "SZZT"
    CUSTOM_CHARSETS.append({
        "id": charset_id,
        "filename": filename,
        "name": name,
        "engine": engine,
    })

CUSTOM_CHARSETS.sort(key=lambda charset: charset["name"].lower())

exe_names = {
    "szzt.zip": "Super ZZT v2.0 (Registered)",
    "wozzt356.zip": "Worlds of ZZT v3.56",
    "zzt.zip": "ZZT v3.2 (Registered)",
    "zzt20.zip": "ZZT v2.0 (Shareware)",
    "zzt30.zip": "ZZT v3.0 (Shareware)",
    "zzt31.zip": "ZZT v3.1 (Shareware)",
    "zzt32sw.zip": "ZZT v3.2 (Shareware)",
    "czoo413-moz.zip": "ClassicZoo v4.13",
    "cleenzzt-moz.zip": "CleenZZT",
}
ZETA_EXECUTABLES = []
exes = sorted(glob.glob(
    os.path.join(
        SITE_ROOT, "museum_site", "static", "data", "zeta86_engines",
        "*.[zZ][iI][pP]"
    )
))
for exe in exes:
    filename = os.path.basename(exe)
    ZETA_EXECUTABLES.append({
        "filename": filename,
        "name": exe_names.get(filename, filename)
    })

ZETA_EXECUTABLES.sort(key=lambda executable: executable["name"].lower())
ZETA_RESTRICTED = 20  # Zeta Config ID used to restrict the use of Zeta

ASCII_UNICODE_CHARS = (
    " ☺☻♥♦♣♠•◘○◙♂♀♪♫☼"
    "►◄↕‼¶§▬↨↑↓→←∟↔▲▼"
    " !\"#$%&'()*+,-./"
    "0123456789:;<=>?"
    "@ABCDEFGHIJKLMNO"
    "PQRSTUVWXYZ[\\]^_"
    "`abcdefghijklmno"
    "pqrstuvwxyz{|}~⌂"
    "ÇüéâäàåçêëèïîìÄÅ"
    "ÉæÆôöòûùÿÖÜ¢£¥₧ƒ"
    "áíóúñÑªº¿⌐¬½¼¡«»"
    "░▒▓│┤╡╢╖╕╣║╗╝╜╛┐"
    "└┴┬├─┼╞╟╚╔╩╦╠═╬╧"
    "╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀"
    "ɑϐᴦᴨ∑ơµᴛɸϴΩẟ∞∅∈∩"
    "≡±≥≤⌠⌡÷≈°∙·√ⁿ²■ "
)

# Patreon Tiers IDs
TIER_NONE = "0"
TIER_CHAR_2 = "659278"  # $2
TIER_5_PURPLE_KEYS = "659279"  # $5
TIER_ZZT_RIVER = "6848286"  # $20
TIER_BOARD_SIZE = "659281"  # $20
TIER_THROWSTAR_SEEK = "6848302"  # $30
TIER_HEALTH = "659282"  # $50
TIER_BRIBE_THE_MAYOR = "659283"  # $100
TIER_NAMES = {
    TIER_NONE: "No tier selected",
    TIER_CHAR_2: "Char 2",
    TIER_5_PURPLE_KEYS: "5 Purple Keys",
    TIER_ZZT_RIVER: "ZZT River Stream",
    TIER_BOARD_SIZE: "20 KB Board Size",
    TIER_THROWSTAR_SEEK: "Throwstar Seek",
    TIER_HEALTH: "?HEALTH",
    TIER_BRIBE_THE_MAYOR: "Bribe the Mayor..."
}

EXTENSION_HINTS = {
    # ZZT
    ".BRD": ("Board File", [DETAIL_ZZT_BOARD], "OR"),
    ".ZZT": ("ZZT World", [DETAIL_ZZT]),
    ".Z_T": ("ZZT World", [DETAIL_ZZT]),
    ".HI": ("High Score File", [DETAIL_ZZT_SCORE], "OR"),
    ".MH": ("Mystical Winds ZZT High Score File", [DETAIL_ZZT_SCORE], "AND"),
    ".MWZ": ("Mystical Winds ZZT World", [DETAIL_ZZT]),
    ".SAV": ("Saved Game", [DETAIL_ZZT_SAVE]),

    # Super ZZT
    ".SZT": ("Super ZZT World", [DETAIL_SZZT]),
    ".HGS": ("Super ZZT High Score File", [DETAIL_SZZT_SCORE]),

    # Custom Charsets
    ".CHR": ("Charset", [DETAIL_GFX]),
    ".COM": ("Charset MAYBE", [DETAIL_GFX]),
    ".FNT": ("Charset", [DETAIL_GFX]),

    # Custom Palettes
    ".PAL": ("Palette", [DETAIL_GFX]),
    ".PLD": ("Palette", [DETAIL_GFX]),

    # ZIG
    ".INF": ("ZIG Information File", [DETAIL_ZIG]),
    ".ZIG": ("ZIG World", [DETAIL_ZIG]),
    ".ZBR": ("ZIG Board", [DETAIL_ZIG]),
    ".ZCH": ("ZIG Charset", [DETAIL_ZIG]),
    ".ZPL": ("ZIG Palette", [DETAIL_ZIG]),
    ".OLF": ("ZIG Object Library", [DETAIL_ZIG]),

    # ZZMs
    ".ZZM": ("ZZM Audio", [DETAIL_ZZM]),

    # ZZT Clone World
    ".ZZ3": ("ZZ3 World", [DETAIL_CLONE_WORLD]),
    ".SWW": ("SuperWAD World", [DETAIL_CLONE_WORLD]),
    ".PGF": ("Plastic Game File", [DETAIL_CLONE_WORLD]),  # Plastic Game File
    ".PWORLD": ("Plastic Game File", [DETAIL_CLONE_WORLD]),  # Platic World

    # Source Code
    ".ASM": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".BAS": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".BI": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".C": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".CC": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".CPP": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".E": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".EX": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".JAVA": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".INC": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".JSON": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".LUA": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".PAS": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".PY": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),

    # Text
    ".135": ("Text File", [DETAIL_TEXT], "AND"),
    ".ASC": ("Text File", [DETAIL_TEXT], "AND"),
    "ASP": ("Text File", [DETAIL_TEXT], "AND"),
    ".1ST": ("Text File", [DETAIL_TEXT], "AND"),
    ".ANS": ("Text File", [DETAIL_TEXT], "AND"),
    ".BAT": ("Batch File", [DETAIL_TEXT]),
    ".BB": ("Text File", [DETAIL_TEXT], "AND"),
    ".CFG": ("Text File", [DETAIL_TEXT], "AND"),
    "COPYING": ("Text File", [DETAIL_TEXT], "AND"),
    ".CRD": ("Text File", [DETAIL_TEXT], "AND"),
    ".DAT": ("Text File", [DETAIL_TEXT], "AND"),  # MIGHT NOT BE VIEWABLE
    "DESC": ("Text File", [DETAIL_TEXT], "AND"),
    ".DEF": ("Text File", [DETAIL_TEXT], "AND"),  # Z2 element defintions
    ".DEU": ("Text File", [DETAIL_TEXT], "AND"),
    ".DIZ": ("Text File", [DETAIL_TEXT], "AND"),
    ".DOC": ("Text File", [DETAIL_TEXT], "AND"),
    ".EED": ("Text File", [DETAIL_TEXT], "AND"),  # ZZT: The Next Generation
    ".ENG": ("Text File", [DETAIL_TEXT], "AND"),
    ".ERR": ("Text File", [DETAIL_TEXT], "AND"),
    "EXCLUDE": ("Text File", [DETAIL_TEXT], "AND"),
    ".FAQ": ("Text File", [DETAIL_TEXT], "AND"),
    ".FLG": ("Text File", [DETAIL_TEXT], "AND"),
    ".FRM": ("Text File", [DETAIL_TEXT], "AND"),
    ".FYI": ("Text File", [DETAIL_TEXT], "AND"),
    ".GITIGNORE": ("Text File", [DETAIL_TEXT], "AND"),
    ".GUD": ("Text File", [DETAIL_TEXT], "AND"),
    ".H": ("Text File", [DETAIL_TEXT], "AND"),
    "HINTS": ("Text File", [DETAIL_TEXT], "AND"),  # Hints?
    ".HLP": ("Text File", [DETAIL_TEXT], "AND"),  # TODO Might not be plaintxt
    ".INI": ("Text File", [DETAIL_TEXT], "AND"),
    ".KB": ("Text File", [DETAIL_TEXT], "AND"),
    "LASTSG": ("Text File", [DETAIL_TEXT], "AND"),
    "LICENSE": ("Text File", [DETAIL_TEXT], "AND"),  # License detail?
    "LPT1": ("Text File", [DETAIL_TEXT], "AND"),
    ".LOG": ("Text File", [DETAIL_TEXT], "AND"),
    ".LST": ("Text File", [DETAIL_TEXT], "AND"),
    ".MAC": ("Text File", [DETAIL_TEXT], "AND"),
    ".MAP": ("Text File", [DETAIL_TEXT], "AND"),
    ".MD": ("Text File", [DETAIL_TEXT], "AND"),
    ".ME": ("Text File", [DETAIL_TEXT], "AND"),
    ".MSG": ("Text File", [DETAIL_TEXT], "AND"),
    ".MUZ": ("Text File", [DETAIL_TEXT], "AND"),
    ".NEW": ("Text File", [DETAIL_TEXT], "AND"),
    "NEWS": ("Text File", [DETAIL_TEXT], "AND"),
    ".NFO": ("Text File", [DETAIL_TEXT], "AND"),
    ".NOW": ("Text File", [DETAIL_TEXT], "AND"),
    ".OBJ": ("Text File", [DETAIL_TEXT], "AND"),
    "ORDER": ("Text File", [DETAIL_TEXT], "AND"),
    ".OOP": ("Text File", [DETAIL_TEXT], "AND"),
    ".PAR": ("Text File", [DETAIL_TEXT], "AND"),
    ".PDF": ("Text File", [DETAIL_TEXT], "AND"),
    "README": ("Text File", [DETAIL_TEXT], "AND"),
    ".REG": ("Text File", [DETAIL_TEXT], "AND"),
    "REGISTER": ("Text File", [DETAIL_TEXT], "AND"),
    ".RTF": ("Text File", [DETAIL_TEXT], "AND"),
    "SAVES": ("Text File", [DETAIL_TEXT], "AND"),
    ".SDI": ("Text File", [DETAIL_TEXT], "AND"),
    ".SH": ("Text File", [DETAIL_TEXT], "AND"),
    ".SOL": ("Text File", [DETAIL_TEXT], "AND"),  # Walkthrough?
    ".SLV": ("Text File", [DETAIL_TEXT], "AND"),  # Walkthrough?
    ".ST": ("Text File", [DETAIL_TEXT], "AND"),
    ".THEME": ("Text File", [DETAIL_TEXT], "AND"),  # Windows 98 Theme
    ".TXT": ("Text File", [DETAIL_TEXT], "AND"),
    "WORLDS": ("Text File", [DETAIL_TEXT], "AND"),
    ".WPS": ("Text File", [DETAIL_TEXT], "AND"),
    ".WRI": ("Text File", [DETAIL_TEXT], "AND"),
    ".ZLN": ("Text File", [DETAIL_TEXT], "AND"),
    ".ZML": ("Text File", [DETAIL_TEXT], "AND"),
    ".ZZL": ("ZZL Object Library", [DETAIL_TEXT], "AND"),

    # HTML
    ".HTM": ("HTML File", [DETAIL_HTML], "AND"),
    ".HTML": ("HTML File", [DETAIL_HTML], "AND"),

    # Audio
    ".IT": ("Audio File", [DETAIL_AUDIO], "AND"),
    ".MID": ("Audio File", [DETAIL_AUDIO], "AND"),
    ".MOD": ("Audio File", [DETAIL_AUDIO], "AND"),
    ".MP3": ("Audio File", [DETAIL_AUDIO], "AND"),
    ".WAV": ("Audio File", [DETAIL_AUDIO], "AND"),
    ".XM": ("Audio File", [DETAIL_AUDIO], "AND"),
    ".PTF": ("Audio File", [DETAIL_AUDIO], "AND"),

    # Image
    ".BMP": ("Image", [DETAIL_IMAGE], "AND"),
    ".GIF": ("Image", [DETAIL_IMAGE], "AND"),
    ".ICO": ("Image", [DETAIL_IMAGE], "AND"),
    ".JPG": ("Image", [DETAIL_IMAGE], "AND"),
    ".PCX": ("Image", [DETAIL_IMAGE], "AND"),
    ".PNG": ("Image", [DETAIL_IMAGE], "AND"),

    # Video
    ".AVI": ("Video", [DETAIL_VIDEO], "AND"),

    # Program
    ".EXE": ("Executable", [DETAIL_PROGRAM], "AND"),
    ".JAR": ("Java Jar", [DETAIL_PROGRAM], "AND"),

    # More Zips
    ".ZIP": ("Compressed File", [DETAIL_COMPRESSED], "AND"),

    # Roms
    ".GBA": ("GBA Rom", [DETAIL_ROM], "AND"),
    ".NES": ("NES Rom", [DETAIL_ROM], "AND"),
    ".PRG": ("TODO_DETAIL_OTHER_FILE", "Miscellaneous File"),  # C64 Program

    # No suggestions
    "/": ("", "IGNORE"),
    ".---": ("?", "IGNORE"),
    ".~~~": ("Organizer", []),
    "._3DSKULL": ("?", []),
    ".ANI": ("Windows Animated Cursor", []),
    ".BIN": ("Binary", []),  # Various (sometimes garbled text files?)
    ".BSV": ("The Draw File", []),
    ".CER": ("?", []),
    ".CORRUPT": ("Known Corrupt File", []),
    ".CUR": ("Windows Cursor", []),
    ".DB": ("?", []),
    ".DLL": ("DLL File", []),
    ".DLM": ("?", []),
    ".DS_STORE": ("OSX Folder Information", []),
    ".GITIGNORE": ("?", []),
    ".LNK": ("Link File", []),
    ".MS": ("?", []),  # Weird file in "Trash Fleet 3.0"
    ".OBJ": ("?", []),  # pazzt
    ".OZ": ("?", []),
    ".PIF": ("Windows Shortcut", []),
    ".SCR": ("BSV2BRD", []),
    ".TRS": ("?", []),  # Weird file in "Operation Blundabo"
    ".VSP": ("?", []),
    ".WAR": ("?", []),
    ".ZR": ("?", []),
}

# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
LANGUAGES = {
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "no": "Norwegian",
    "pl": "Polish",
    "es": "Spanish",
    "xx": "Other"
}

LANGUAGE_CHOICES = tuple(LANGUAGES.items())

LICENSE_CHOICES = [
    ("UNK", "Unknown"),
    ("PD", "Public Domain"),
    ("MIT", "MIT License"),
    ("GPL", "GNU General Public License"),
    ("CC", "Creative Commons"),
    ("AUTH", "Author Defined"),
    ("ARR", "All Rights Reserved")
]

LICENSE_SOURCE_CHOICES = [
    ("NONE", "None"),
    ("LICENSE", "License File"),
    ("DOCS", "Documentation File"),
    ("WORLD", "World File"),
]
