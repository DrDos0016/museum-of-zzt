import base64
import uuid
import zipfile
import binascii
import base64
import os

from io import BytesIO

from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from PIL import Image
from markdown_deux.templatetags import markdown_deux_tags

from .models import *
from .common import *


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
    except NotImplementedError as error:
        print(filename)
        return HttpResponse("Unimplemented Compression Method:" + str(error))
    except Exception as error:
        print(filename)
        print(type(error))
        print(error)
        return HttpResponse(
            "An error occurred, and the file could not be retreived."
        )

    if ext in (FILE_VIEWER_TEXT_EXTENSIONS):
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
            "&", "&amp;"
        ).replace(
            "<", "&lt;"
        ).replace(
            ">", "&gt;"
        )

        output = ("<div class='text-file {}'>"
                  "<pre class='cp437'>{}</pre></div>").format(encoding, output)
        return HttpResponse(output)
    elif ext in (FILE_VIEWER_HEX_EXTENSIONS):
        return HttpResponse(binascii.hexlify(file.read()))
    elif ext in (FILE_VIEWER_B64_EXTENSIONS):
        b64 = base64.b64encode(file.read())
        return HttpResponse(b64)
    elif ext in (FILE_VIEWER_AUDIO_EXTENSIONS):
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
        return HttpResponse(
            "This file type is not currently supported for embedded content."
        )


def deep_search(request, phase):
    phase = int(phase)
    if phase == 1:
        title = request.GET.get("title")
        author = request.GET.get("author")
        query = request.GET.get("query")

        qs = File.objects.all()
        if title:
            qs = qs.filter(title__icontains=title)
        if author:
            qs = qs.filter(author__icontains=author)

        count = qs.count()

        print("QS contains...")
        for f in qs:
            print(f)

    return HttpResponse(
        "Criteria narrowed to {} files. Beginning search.".format(count)
    )


def debug_file(request):
    if not os.path.isfile("/var/projects/DEV"):
        return HttpResponse("Not on production.")
    file = open(request.GET.get("file"), "rb")
    return HttpResponse(binascii.hexlify(file.read()))


def render_review_text(request):
    output = request.POST.get("text", "")
    if output:
        output = markdown_deux_tags.markdown_filter(output)
    return HttpResponse(output)


@staff_member_required
def wozzt_queue_add(request):
    resp = "SUCCESS"
    d = request.POST
    e = WoZZT_Queue()

    # Create queue object
    try:
        e.file_id = int(d["file_id"])
        e.zzt_file = d["zzt_file"]
        e.board = int(d["board"])
        e.board_name = d["board_name"]
        e.dark = d["dark"]
        e.zap = int(d["zap"])
        e.shot_limit = int(d["shot_limit"])
        e.time_limit = int(d["time_limit"])
        e.category = d["category"]
        e.priority = int(d["priority"])
        e.uuid = str(uuid.uuid4())
    except ValueError:
        resp = "FAILED"

    # Save image
    raw = d["b64img"].replace("data:image/png;base64,", "", 1)

    image = Image.open(BytesIO(base64.b64decode(raw)))
    filepath = os.path.join(
        SITE_ROOT, "museum_site", "static", "wozzt-queue", e.uuid + ".png"
    )

    image.save(filepath)
    e.save()

    return HttpResponse(resp)
