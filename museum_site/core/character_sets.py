import glob
import os

from museum_site.constants import CHARSET_PATH

# Character Sets
def init_charsets(site_root):
    standard_charsets = [
        {"id": 0, "filename": "cp437.png", "name": "Code Page 437", "engine": "ZZT"},
        {"id": 0, "filename": "szzt-cp437.png", "name": "Code Page 437 (SZZT)", "engine": "SZZT"},
    ]

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
    return (standard_charsets, custom_charsets)
