import glob
import os

from django.conf import settings
from django.core.cache import cache

from museum_site.constants import CHARSET_PATH

# Character Sets
def init_standard_charsets():
    standard_charsets = [
        {"id": 0, "filename": "cp437.png", "name": "Code Page 437", "engine": "ZZT"},
        {"id": 0, "filename": "szzt-cp437.png", "name": "Code Page 437 (SZZT)", "engine": "SZZT"},
    ]
    cache.set("CHARSETS", standard_charsets)

def init_custom_charsets():
    # Pull custom charsets
    custom_charsets = []

    pngs = sorted(glob.glob(os.path.join(CHARSET_PATH, "*.png")))
    for png in pngs:
        filename = os.path.basename(png)
        if filename.find("cp437") != -1:  # Skip standard charsets
            continue
        if filename.startswith("szzt"):
            charset_id = int(filename.split("-")[1])
        else:
            charset_id = int(filename.split("-")[0])

        name = filename.split("-")[-1][:-4]
        engine = "ZZT" if "szzt" not in filename else "SZZT"
        custom_charsets.append({"id": charset_id, "filename": filename, "name": name, "engine": engine})

    custom_charsets.sort(key=lambda charset: charset["name"].lower())
    cache.set("CUSTOM_CHARSETS", custom_charsets)
