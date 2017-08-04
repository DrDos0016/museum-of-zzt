from django.http import HttpResponse

from .models import *
from .common import *

import zipfile
import binascii
import base64
import os


def get_zip_file(request):
    letter = request.GET.get("letter")
    zip = request.GET.get("zip")
    filename = request.GET.get("filename", "")
    format = request.GET.get("format", "auto")
    ext = os.path.splitext(filename.lower())[1]
    uploaded = request.GET.get("uploaded", "false")
    if filename.find(".") == -1:
        ext = ".txt"

    if uploaded != "false":
        letter = "uploaded"

    try:
        zip = zipfile.ZipFile(os.path.join(SITE_ROOT, "zgames", letter, zip))
        file = zip.open(filename)

    except Exception as error:
        print(filename)
        print(type(error))
        print(error)
        return HttpResponse(
            "An error occurred, and the file could not be retreived."
        )

    if ext in ("", ".txt", ".bat", ".cfg", ".nfo", ".dat", ".bas", ".deu", ".diz", ".c", ".ds_store", ".faq", ".frm", ".fyi", ".gud", ".h", ".hlp", ".lst", ".me", ".nfo", ".pas", ".reg", ".sol", ".zln", ".zml", ".zzl", ".zzm", ".135", ".1st", ".asm", ".bb", ".bin", ".chr", ".sdi", ".now"):
        output = file.read()

        if format == "auto" or format == "utf-8":
            try:
                output = output.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError as e:
                output = output.decode("cp437")
                encoding = "cp437"
        elif format == "cp437":
            output = output.decode("cp437")
            encoding = "cp437"
        elif format == "hex":
            output = "HEXADECIMAL"
            encding = "hex"

        output = output.replace(
            "\r\n", "<br>"
        ).replace(
            "\r", "<br>"
        ).replace(
            "\n", "<br>"
        ).replace(
            "  ", " &nbsp;"
        )
        output = "<div class='" + encoding + "'>" + output + "</div>"

        return HttpResponse(output)
    elif ext in (".hi", ".zzt", ".brd", ".mh", ".sav", ".szt"):
        return HttpResponse(binascii.hexlify(file.read()))
    elif ext in (".jpg", ".jpeg", ".bmp", ".gif", ".png", ".ico", ".avi"):
        b64 = base64.b64encode(file.read())
        return HttpResponse(b64)
    elif ext in (".wav", ".mp3", ".ogg", ".mid", ".midi"):
        response = HttpResponse(file.read())

        if ext == ".wav":
            response["Content-Type"] = "audio/wav wav"
        elif ext == ".mp3":
            response["Content-Type"] = "audio/mpeg mp3"
        elif ext == ".ogg":
            response["Content-Type"] = "audio/ogg ogg"
        else:  # Fallback
            response["Content-Type"] = "application/octet-stream"

        return response
    else:
        return HttpResponse("Maybe in the future")

def debug_file(request):
    if not os.path.isfile("/var/projects/DEV"):
        return HttpResponse("Not on production.")
    file = open(request.GET.get("file"), "rb")
    return HttpResponse(binascii.hexlify(file.read()))
