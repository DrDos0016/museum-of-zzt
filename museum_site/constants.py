import glob
import os

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
TERMS = """
MUSEUM OF ZZT USER ACCOUNT TERMS (v.2021.06.14)

Oops this isn't quite ready yet.

But the gist will be to ensure that your contributions to this community
result in a welcoming, helpful, and inclusive environment.
"""
TOKEN_EXPIRATION_SECS = 600

# Admin information
ADMIN_NAME = "Dr. Dos"

# Host/Environment information
if os.path.isfile(os.path.join(SITE_ROOT, "PROD")):
    URL_ROOT = "https://museumofzzt.com/"
    PROTOCOL = "https"
    DOMAIN = "museumofzzt.com"
    ENV = "PROD"
elif os.path.isfile(os.path.join(SITE_ROOT, "DEV")):
    HOST = "http://django.pi:8000/"
    PROTOCOL = "http"
    DOMAIN = "django.pi"
    ENV = "DEV"
elif os.path.isfile(os.path.join(SITE_ROOT, "BETA")):
    HOST = "https://beta.museumofzzt.com/"
    PROTOCOL = "https"
    DOMAIN = "beta.museumofzzt.com"
    ENV = "BETA"

# Article publish states
PUBLISHED_ARTICLE = 1
UPCOMING_ARTICLE = 2
UNPUBLISHED_ARTICLE = 3
REMOVED_ARTICLE = 0

# Upload contact settings
UPLOAD_CONTACT_NONE = 0
UPLOAD_CONTACT_REJECTION = 1
UPLOAD_CONTACT_ALL = 2

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

# Front Page
FP_ARTICLES_SHOWN = 10
FP_NEW_RELEASES_SHOWN = 12
FP_FILES_SHOWN = 12
FP_REVIEWS_SHOWN = 10

# File categories
CATEGORY_LIST = (
    ("?", "?"),
    ("MS-DOS", "MS-DOS Programs"),
    ("WIN16", "16-Bit Windows Programs"),
    ("WIN32", "32-Bit Windows Programs"),
    ("WIN64", "64-Bit Windows Programs"),
    ("LINUX", "Linux Programs"),
    ("OSX", "OSX Programs"),
    ("FEATURED", "Featured Worlds"),
    ("UNUSED-8", "UNUSED Contest Entries"),
    ("ZZM", "ZZM Soundtracks"),
    ("GFX", "Modified Graphics"),
    ("MOD", "Modified Executables"),
    ("ETC", "Etc."),
    ("SZZT", "Super ZZT Worlds"),
    ("UTILITY", "Utilities"),
    ("ZZT", "ZZT Worlds"),
    ("ZIG", "ZIG Worlds"),
    ("LOST", "Lost Worlds"),
    ("UPLOADED", "Uploaded Worlds"),
    ("REMOVED", "Removed Worlds"),
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

LOCKED_ARTICLE_TEXT = """
<h2>Locked Article!</h2>

<p>The article you have requested is currently only available to patrons
making a monthly pledge to the Worlds of ZZT Patreon of at least <b>$[COST]
USD</b> per month.</p>

<p>If you are a patron that meets these requirements you can enter your
password to access this article in the field below:</p>

<p><form>
<input name="secret" type="password" value="">
<input type="submit" value="Unlock">
</form></p>

If you need your password please see the
<a href="{% url 'patron_articles' %}">early articles</a> page for instructions.

<p>All articles published on the Museum of ZZT are eventually made public. The
estimated release date for this article is <b>[RELEASE]</b>, however the exact
release date may change.</p>"""

EXTENSION_HINTS = {
    # ZZT
    ".BRD": ("Board File", [DETAIL_ZZT_BOARD], "OR"),
    ".ZZT": ("ZZT World", [DETAIL_ZZT]),
    ".Z_T": ("ZZT World", [DETAIL_ZZT]),
    ".HI": ("High Score File", [DETAIL_ZZT_SCORE], "OR"),
    ".MH": ("High Score File", [DETAIL_ZZT_SCORE], "AND"),
    ".MWZ": ("Mystic Winds ZZT World", [DETAIL_ZZT]),
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
    ".SWW": ("??? World", [DETAIL_CLONE_WORLD]),
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
    ".OBJ": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),  # Maybe
    ".PAS": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),
    ".PY": ("Source Code", [DETAIL_SOURCE_CODE], "AND"),

    # Text
    ".135": ("Text File", [DETAIL_TEXT], "AND"),
    ".ASC": ("Text File", [DETAIL_TEXT], "AND"),
    "ASP": ("Text File", [DETAIL_TEXT], "AND"),
    ".1ST": ("Text File", [DETAIL_TEXT], "AND"),
    ".ANS": ("Text File", [DETAIL_TEXT], "AND"),
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
    ".FRM": ("Text File", [DETAIL_TEXT], "AND"),
    ".FYI": ("Text File", [DETAIL_TEXT], "AND"),
    ".GITIGNORE": ("Text File", [DETAIL_TEXT], "AND"),
    ".GUD": ("Text File", [DETAIL_TEXT], "AND"),
    ".H": ("Text File", [DETAIL_TEXT], "AND"),
    "HINTS": ("Text File", [DETAIL_TEXT], "AND"),  # Hints?
    ".HLP": ("Text File", [DETAIL_TEXT], "AND"),  # TODO Might not be plaintxt
    ".INI": ("Text File", [DETAIL_TEXT], "AND"),
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
    "ORDER": ("Text File", [DETAIL_TEXT], "AND"),
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
    ".BAT": ("Batch File", []),
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
    ".OZ": ("?", []),
    ".PIF": ("Windows Shortcut", []),
    ".SCR": ("BSV2BRD", []),
    ".TRS": ("?", []),  # Weird file in "Operation Blundabo"
    ".VSP": ("?", []),
    ".WAR": ("?", []),
    ".ZR": ("?", []),
}
