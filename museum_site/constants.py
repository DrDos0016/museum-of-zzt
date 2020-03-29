import os

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Patron Locked Content
try:
    from museum_site.patron_secrets import PASSWORD2DOLLARS, PASSWORD5DOLLARS
except ModuleNotFoundError:
    print("PATRON_SECRETS.PY NOT FOUND. USING DEV VALUES")
    PASSWORD2DOLLARS = "test2dollars"
    PASSWORD5DOLLARS = "test5dollars"

# Article publish states
PUBLISHED_ARTICLE = 1
UPCOMING_ARTICLE = 2
UNPUBLISHED_ARTICLE = 3
REMOVED_ARTICLE = 0

# File details
DETAIL_DOS = 1
DETAIL_WIN16 = 2
DETAIL_WIN32 = 3
DETAIL_WIN64 = 4
DETAIL_LINUX = 5
DETAIL_OSX = 6
DETAIL_FEATURED = 7
DETAIL_CONTEST = 8
DETAIL_ZZM = 9
DETAIL_GFX = 10
DETAIL_MOD = 11
DETAIL_ETC = 12
DETAIL_SZZT = 13
DETAIL_UTILITY = 14
DETAIL_ZZT = 15
DETAIL_ZIG = 16
DETAIL_LOST = 17
DETAIL_UPLOADED = 18
DETAIL_REMOVED = 19

# Front Page
FP_ARTICLES_SHOWN = 10
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
