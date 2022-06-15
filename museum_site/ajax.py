import base64
import uuid
import zipfile
import binascii
import base64
import os

from io import BytesIO

from django.http import HttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from PIL import Image
from markdown_deux.templatetags import markdown_deux_tags

from museum_site.models import *
from museum_site.common import *


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
        record(filename)
        return HttpResponse("Unimplemented Compression Method:" + str(error), status=501)
    except Exception as error:
        record(filename)
        record(type(error))
        record(error)
        return HttpResponse(
            "An error occurred, and the file could not be retreived.", status=404
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
    elif ext == ".pld":
        return HttpResponse(parse_pld(file.read()))
    else:
        return HttpResponse(
            "This file type is not currently supported for embedded content.", status=501
        )


def debug_file(request):
    if not os.path.isfile("/var/projects/DEV"):
        return HttpResponse("Not on production.")
    if request.GET.get("file"):
        file = open(request.GET["file"], "rb")
        return HttpResponse(binascii.hexlify(file.read()))
    else:
        return HttpResponse("No file provided.")


def get_author_suggestions(request, max_suggestions=20):
    query = request.GET.get("q", "")
    output = {"suggestions": []}

    if query:
        qs = File.objects.filter(author__istartswith=query).only("author").distinct().order_by("author")
        for f in qs:
            all_authors = f.author.split("/")
            for a in all_authors:
                if a not in output["suggestions"]:
                    output["suggestions"].append(a)
            if len(output["suggestions"]) >= max_suggestions:
                break

        if len(output["suggestions"]) < max_suggestions:
            qs = File.objects.filter(author__icontains=query).only("author").distinct().order_by("author")
            for f in qs:
                all_authors = f.author.split("/")
                for a in all_authors:
                    if a not in output["suggestions"]:
                        output["suggestions"].append(a)
                if len(output["suggestions"]) >= max_suggestions:
                    break

    return JsonResponse(output)


def get_company_suggestions(request, max_suggestions=20):
    query = request.GET.get("q", "")
    output = {"suggestions": []}

    if query:
        qs = File.objects.filter(company__istartswith=query).only("company").distinct().order_by("company")
        for f in qs:
            all_companies = f.company.split("/")
            for c in all_companies:
                if c not in output["suggestions"]:
                    output["suggestions"].append(c)
            if len(output["suggestions"]) >= max_suggestions:
                break

        if len(output["suggestions"]) < max_suggestions:
            qs = File.objects.filter(company__icontains=query).only("company").distinct().order_by("company")
            for f in qs:
                all_companies = f.company.split("/")
                for c in all_companies:
                    if c not in output["suggestions"]:
                        output["suggestions"].append(c)
                if len(output["suggestions"]) >= max_suggestions:
                    break

    return JsonResponse(output)


def get_search_suggestions(request, max_suggestions=25):
    query = request.GET.get("q", "")
    output = {"suggestions": []}

    if query:
        qs = File.objects.filter(title__istartswith=query).only("title").distinct().order_by("sort_title")
        for f in qs:
            if f.title not in output["suggestions"]:
                output["suggestions"].append(f.title)
            if len(output["suggestions"]) >= max_suggestions:
                break

        if len(output["suggestions"]) < max_suggestions:
            qs = File.objects.filter(title__icontains=query).only("title").distinct().order_by("sort_title")

            for f in qs:
                if f.title not in output["suggestions"]:
                    output["suggestions"].append(f.title)
                if len(output["suggestions"]) >= max_suggestions:
                    break
    return JsonResponse(output)


def render_review_text(request):
    # output = profanity_filter(request.POST.get("text", ""))
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
