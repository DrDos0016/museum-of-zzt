import glob
import os

from collections import namedtuple
from datetime import datetime

DEBUG = True if os.path.isfile("/var/projects/DEV") else False  # Debug mode

# Times and Dates
START_TIME = datetime.utcnow()
BOOT_TS = START_TIME.strftime("%m%d%H%M%S")
YEAR = datetime.now().year

# Paths
SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /var/projects/museum-of-zzt
TEMP_PATH = os.path.join(SITE_ROOT, "temp")  # /var/projects/museum-of-zzt/temp
STATIC_PATH = os.path.join(SITE_ROOT, "museum_site", "static")  # /var/projects/museum-of-zzt/museum_site/static

# Contact Information
EMAIL_ADDRESS = "doctordos@gmail.com"

# Play Online Options
PLAY_METHODS = {"archive": {"name": "Archive.org - DosBox Embed"}, "zeta": {"name": "Zeta"}}

# Global CSS Files
CSS_INCLUDES = ["museum-site.css", "main.css", "zzt.css", "low-res.css", "forms.css", "model-blocks.css"]

# Private settings - (Patron Locked Content, IA API)
try:
    from museum_site.private import PASSWORD2DOLLARS, PASSWORD5DOLLARS, IA_ACCESS, IA_SECRET, BANNED_IPS
    IA_SUPPORT = True
except ModuleNotFoundError:
    print("PRIVATE.PY NOT FOUND. USING DEV VALUES")
    PASSWORD2DOLLARS = "test2dollars"
    PASSWORD5DOLLARS = "test5dollars"
    IA_ACCESS = "Not found"
    IA_SECRET = "Not found"
    IA_SUPPORT = False
    BANNED_IPS = [""]

# Pagination
PAGE_SIZE = 25  # Default items per page
LIST_PAGE_SIZE = 250  # Default items per page in LIST view
NO_PAGINATION = 9999  # Actual limit with "Unlimited" items per page
PAGE_LINKS_DISPLAYED = 30  # Number of links to other pages displayed

# Site Functions
UPLOADS_ENABLED = True
UPLOAD_CAP = 1048576  # 1 Megabyte (unless manually increased per user)
UPLOAD_TEST_MODE = False  # Coerce successful uploads in DEV to expedite testing of the upload process
MODEL_BLOCK_VERSION = 2023

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
User passwords are stored in a hashed and salted format preventing anyone from easily acquiring them. Nevertheless using a unique password is strongly encouraged as the Museum of ZZT and its security are essentially a one person operation.

On occasion to better facilitate site development the Museum of ZZT's database is exported, scrubbed, and published to be used as a starting point for development. The scrubbing process includes data being blanked out or replaced with dummy data. This includes IP addresses, email addresses, all session data, password hashes, and profile information.

Because some data is captured in these database dumps it is possible for deleted information to still be available. When submitting data to the Museum of ZZT, please consider that there is a possibility that it is never truly gone forever when erased from the live site.

By accepting these terms of service you are acknowledging the potential for your data to persist in potentially unforeseen ways, and providing permission for that data to be stored, shared, and reproduced in Worlds of ZZT projects.

## Email
Your email address (and patron email address) will not be shared with third parties. A valid email address is required to verify your account and provide password reset functionality.

By accepting these terms of service you are providing permission to store this information within the Museum of ZZT's database.

## Patronage
Users will have their account's email address or a specifically chosen Patreon email address cross-referenced against a nightly generated list of active Worlds of ZZT patrons. If a match is found your account will be marked as a patron with the current pledge and selected tier recorded. This information is used to allow users to access patron exclusive perks based on these values.

At the time of writing, accounts which no longer remain patrons either due to denied payments or canceled pledges will not automatically lose their patron status.

By accepting these terms of service you are providing permission to link your Museum of ZZT account to Worlds of ZZT Patreon information and storing relevant data about your patronage to provide access to patron exclusive content and site functionality.

## User Conduct
It is a goal of the Worlds of ZZT project to help create and foster a ZZT community which is welcoming and inclusive to all regardless of age, race, gender, ZZT experience, religion, orientation, etc. Users and guests contributing to this community are expected to do so in a way which aligns with this goal.

Do not abuse functionality to alter your username. Impersonating other users or using characters to adversely affect (successfully or otherwise) page rendering are strictly forbidden.

Users are expected to abide by all Museum rules and policies when uploading files, posting reviews, and leaving comments.

Users are expected to be respectful of other community members and privately contact staff when there is an issue either through direct messages on Discord or via email.

By accepting these terms of service you are agreeing to conduct yourself in a manner that aligns with these ideals.

## Violations Violations of these terms may result in you and/or your account having permissions to participate in certain site functions (including but not limited to uploading files, posting reviews, participating on the Worlds of ZZT Discord) being revoked for any amount of time felt necessary.

By accepting these terms of service you are acknowledging and agreeing to the consequences of violating these terms.
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
elif os.path.isfile(os.path.join(SITE_ROOT, "BETA")):
    HOST = "https://beta.museumofzzt.com/"
    PROTOCOL = "https"
    DOMAIN = "beta.museumofzzt.com"
    ENV = "BETA"
else:  # DEV
    HOST = "http://django.pi:8000/"
    PROTOCOL = "http"
    DOMAIN = "django.pi:8000"
    ENV = "DEV"

# Magic Numbers
UPCOMING_ARTICLE_MINIMUM_PATRONAGE = 200
UNPUBLISHED_ARTICLE_MINIMUM_PATRONAGE = 500

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

# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
LANGUAGES = {
    "cs": "Czech",
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

# File Viewer v1.0 Extensions
FILE_VIEWER_TEXT_EXTENSIONS = (
    "", ".135", ".135.asc", ".1st", ".ans", ".asm", ".bas", ".bat", ".bb",
    ".bi", ".bin", ".c", ".cc", ".cfg", ".chr", ".cpp", ".crd", ".dat", ".def",
    ".deu", ".diz", ".doc", ".ds_store", ".e", ".eed", ".eng", ".err", ".ex",
    ".faq", ".frm", ".fyi", ".gitignore", ".gud", ".h", ".hlp", ".inc", ".inf",
    ".ini", ".java", ".json", ".log", ".lst", ".lua", ".mac", ".map", ".md",
    ".me", ".msg", ".muz", ".new", ".nfo", ".now", ".obj", ".olf", ".pas", ".py",
    ".reg", ".rtf", ".sdi", ".sh", ".slv", ".sol", ".st", ".theme", ".txt",
    ".wps", ".wri", ".zln", ".zml", ".zzl", ".zzm",
)
FILE_VIEWER_HEX_EXTENSIONS = (".hi", ".zzt", ".brd", ".mh", ".sav", ".szt", ".mwz", ".z_t", ".hgs",)
FILE_VIEWER_B64_EXTENSIONS = (".jpg", ".jpeg", ".bmp", ".gif", ".png", ".ico", ".avi")
FILE_VIEWER_AUDIO_EXTENSIONS = (".wav", ".mp3", ".ogg", ".mid", ".midi")


# Form related constants
FORM_ANY = "- Any -"
FORM_NONE = "- None -"

# Date/Time Formats
DATE_HR = "%b %d, %Y" # ex: "Mar 05, 2023"
DATE_NERD = "%Y-%m-%d"  # ex: "2010-02-06"
DATE_FULL = "%b %d, %Y, %I:%M:%S %p"  # ex: "Nov 06, 2022, 08:06:03 PM"
