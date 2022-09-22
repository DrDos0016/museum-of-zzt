import os
import urllib.parse
import zipfile

from django.shortcuts import render, get_object_or_404

from museum_site.common import *
from museum_site.constants import *
from museum_site.core import *
from museum_site.models import *


@rusty_key_check
def file_attributes(request, key):
    data = {}
    data["file"] = get_object_or_404(File, key=key)
    data["file"].init_actions()
    data["upload_info"] = Upload.objects.get(file_id=data["file"])
    data["reviews"] = Review.objects.filter(zfile__id=data["file"].pk).defer("content")
    data["title"] = data["file"].title + " - Attributes"
    return render(request, "museum_site/attributes.html", data)


@rusty_key_check
def file_download(request, key):
    """ Returns page listing all download locations with a provided file """
    data = {}
    data["file"] = get_object_or_404(File, key=key)
    data["title"] = data["file"].title + " - Downloads"
    data["downloads"] = data["file"].downloads.all()
    data["letter"] = data["file"].letter
    return render(request, "museum_site/download.html", data)


@rusty_key_check
def file_viewer(request, key, local=False):
    """ Returns page exploring a file's zip contents """
    data = {
        "content_classes": ["fv-grid"],
        "details": [],
        "local": local,
        "files": [],
    }

    if not local:
        qs = File.objects.filter(key=key)
        if len(qs) == 1:
            data["file"] = qs[0]
        else:
            return redirect("/search?filename={}&err=404".format(key))

        # Check for explicit flag/permissions
        if data["file"].explicit:
            check = explicit_redirect_check(request, data["file"].pk)
            if check != "NO-REDIRECT":
                return check

        data["title"] = data["file"].title
        data["letter"] = data["file"].letter

        # Check for recommended custom charset
        for charset in CUSTOM_CHARSETS:
            if data["file"].id == charset["id"]:
                data["custom_charset"] = charset["filename"]
                break

        if data["file"].is_detail(DETAIL_UPLOADED):
            letter = "uploaded"
            data["uploaded"] = True

        zip_file = zipfile.ZipFile(
            data["file"].phys_path()
        )
        files = zip_file.namelist()
        files.sort(key=str.lower)
        data["zip_info"] = sorted(
            zip_file.infolist(), key=lambda k: k.filename.lower()
        )
        data["zip_comment"] = zip_file.comment.decode("latin-1")
        # TODO: "latin-1" may or may not actually be the case

        # Filter out directories (but not their contents)
        for f in files:
            if (f and f[-1] != os.sep and not f.startswith("__MACOSX" + os.sep) and not f.upper().endswith(".DS_STORE")):
                data["files"].append(f)
        data["load_file"] = urllib.parse.unquote(
            request.GET.get("file", "")
        )
        data["load_board"] = request.GET.get("board", "")
    else:  # Local files
        data["file"] = "Local File Viewer"
        data["letter"] = ""

    # Sort files into ZZT, Super ZZT, SAV, BRD, and non-ZZT extensions
    all_files = {"zzt": [], "szzt": [], "sav": [], "brd": [], "misc": []}
    keys = list(all_files.keys())
    for fname in data["files"]:
        ext = fname.split(".")[-1].lower()
        if ext in keys:
            all_files[ext].append(fname)
        else:
            all_files["misc"].append(fname)
    data["files"] = []
    for k in keys:
        sorted(all_files[k])
        data["files"] += all_files[k]

    data["charsets"] = []
    data["custom_charsets"] = []

    if not data["local"]:
        if data["file"].is_detail(DETAIL_ZZT):
            for charset in CHARSETS:
                if charset["engine"] == "ZZT":
                    data["charsets"].append(charset)
            for charset in CUSTOM_CHARSETS:
                if charset["engine"] == "ZZT":
                    data["custom_charsets"].append(charset)
        elif data["file"].is_detail(DETAIL_SZZT):
            for charset in CHARSETS:
                if charset["engine"] == "SZZT":
                    data["charsets"].append(charset)
            for charset in CUSTOM_CHARSETS:
                if charset["engine"] == "SZZT":
                    data["custom_charsets"].append(charset)
        else:
            data["charsets"] = CHARSETS
            data["custom_charsets"] = CUSTOM_CHARSETS
    # TODO LOCAL FILES CAN'T GET CHARSETS WITH THIS
    else:
        data["charsets"] = CHARSETS
        data["custom_charsets"] = CUSTOM_CHARSETS

    return render(request, "museum_site/file.html", data)


def get_file_by_pk(request, pk):
    f = get_object_or_404(File, pk=pk)
    return redirect(f.attributes_url())
