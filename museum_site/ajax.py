import base64
import json
import uuid
import zipfile
import binascii
import os

from datetime import datetime, UTC

from django.http import HttpResponse, JsonResponse

from museum_site.models import *
from museum_site.constants import *
from museum_site.core.image_utils import open_base64_image
from museum_site.core.misc import extract_file_key_from_url, record, zipinfo_datetime_tuple_to_str
from museum_site.core.palette import parse_pld, parse_pal
from museum_site.templatetags.site_tags import model_block, render_markdown
from museum_site.forms.collection_forms import Collection_Content_Form, Collection_Form
from stream.models import Stream_Entry, Stream


def arrange_collection(request):
    """ Get the latest added file to a collection """
    if not request.POST.get("collection_id"):
        return HttpResponse("")
    # Confirm this is your collection
    c = Collection.objects.get(pk=int(request.POST["collection_id"]))
    if not request.user:
        return HttpResponse("ERROR: Unauthorized user!")
    if request.user and request.user.id != c.user.id:
        return HttpResponse("ERROR: Unauthorized user!")

    collection_id = int(request.POST.get("collection_id"))
    order = request.POST.get("order").split("/")

    entries = Collection_Entry.objects.get_items_in_collection(collection_id)

    for entry in entries:
        entry.order = order.index(str(entry.pk)) + 1
        entry.save()
    c.default_sort = "manual"
    c.save()

    resp = "SUCCESS"
    return HttpResponse(resp)


def get_collection_addition(request):
    """ Get the latest added file to a collection """
    collection_id = int(request.GET.get("collection_id", 0))
    if not collection_id:
        return HttpResponse("")
    entry = Collection_Entry.objects.get_latest_addition_to_collection(collection_id)
    html = model_block({"request": request}, entry)
    return HttpResponse(html)


def get_search_suggestions(request, max_suggestions=25):
    query = request.GET.get("q", "")
    output = {"suggestions": []}

    if query:
        qs = File.objects.basic_search_suggestions(query=query)
        for f in qs:
            if f.title not in output["suggestions"]:
                output["suggestions"].append(f.title)
            if len(output["suggestions"]) >= max_suggestions:
                break

        if len(output["suggestions"]) < max_suggestions:
            qs = File.objects.basic_search_suggestions(query=query, match_anywhere=True)

            for f in qs:
                if f.title not in output["suggestions"]:
                    output["suggestions"].append(f.title)
                if len(output["suggestions"]) >= max_suggestions:
                    break
    return JsonResponse(output)


def get_suggestions_for_field(request, field):
    """ Used on file upload page """
    output = {"suggestions": []}
    model = {"author": Author, "company": Company}.get(field)
    if model is not None:
        qs = model.objects.all().only("title").order_by("title")
        for i in qs:
            output["suggestions"].append(i.title)
        output["suggestions"] = sorted(output["suggestions"], key=lambda s: s.casefold())
    return JsonResponse(output)


def get_zip_file_by_key(request):
    if not request.GET:  # Ask for nothing, receive nothing
        return HttpResponse("")

    zfile = File.objects.get(key=request.GET.get("key"))
    with open(zfile.phys_path(), "rb") as fh:
        output = base64.b64encode(fh.read())
    return HttpResponse(output)


def get_zip_file(request):
    if not request.GET:  # Ask for nothing, receive nothing
        return HttpResponse("")
    letter = request.GET.get("letter")
    zip_file = request.GET.get("zip")
    filename = request.GET.get("filename", "")
    file_format = request.GET.get("format", "auto")
    ext = os.path.splitext(filename.lower())[1]
    uploaded = request.GET.get("uploaded", "false")
    if filename.find(".") == -1:
        ext = ".txt"

    if uploaded != "false":
        letter = "uploaded"

    try:
        zip_file = zipfile.ZipFile(os.path.join(ZGAMES_BASE_PATH, letter, zip_file))
        fh = zip_file.open(filename)
    except NotImplementedError as error:
        record(filename)
        return HttpResponse("Unimplemented Compression Method:" + str(error), status=501)
    except Exception as error:
        record(filename)
        record(type(error))
        record(error)
        return HttpResponse("An error occurred, and the file could not be retreived.", status=404)

    if ext in (FILE_VIEWER_TEXT_EXTENSIONS):
        output = fh.read()

        if file_format == "auto" or file_format == "utf-8":
            try:
                output = output.decode("utf-8")
                encoding = "utf-8"
            except UnicodeDecodeError as e:
                output = output.decode("cp437")
                encoding = "cp437"
        elif file_format == "cp437":
            output = output.decode("cp437")
            encoding = "cp437"
        elif file_format == "hex":
            output = "HEXADECIMAL"
            encding = "hex"

        output = output.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        output = ("<div class='text-file {}'>"
                  "<pre class='cp437'>{}</pre></div>").format(encoding, output)
        return HttpResponse(output)
    elif ext in (FILE_VIEWER_HEX_EXTENSIONS):
        return HttpResponse(binascii.hexlify(fh.read()))
    elif ext in (FILE_VIEWER_B64_EXTENSIONS):
        b64 = base64.b64encode(fh.read())
        return HttpResponse(b64)
    elif ext in (FILE_VIEWER_AUDIO_EXTENSIONS):
        response = HttpResponse(fh.read())

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
        return HttpResponse(parse_pld(fh.read()))
    elif ext == ".pal":
        return HttpResponse(parse_pal(fh.read()))

    return HttpResponse("This file type is not currently supported for embedded content.", status=501)


def otf_get_available_collections(request):
    output = {"collections": []}
    if not request.user:
        return JsonResponse(output)
    if request.user and not request.user.id:
        return JsonResponse(output)

    qs = Collection.objects.filter(user_id=request.user.id).exclude(otf_support=False).only("pk", "title", "visibility").order_by("title")
    for c in qs:
        output["collections"].append({"pk": c.pk, "title": c.title, "visibility": c.visibility_str[:3]})

    request.session["otf_collection_json"] = json.dumps(output)
    request.session["otf_refresh"] = False
    return JsonResponse(output)


def remove_from_collection(request):
    if not request.POST.get("collection_id"):
        return HttpResponse("")
    # Confirm this is your collection
    c = Collection.objects.get(pk=int(request.POST["collection_id"]))
    if not request.user:
        return HttpResponse("ERROR: Unauthorized user!")
    if request.user and request.user.id != c.user.id:
        return HttpResponse("ERROR: Unauthorized user!")

    entry = Collection_Entry.objects.get(
        collection_id=int(request.POST["collection_id"]),
        pk=int(request.POST["zfile_id"]),
    )

    entry.delete()
    # Update count
    c.item_count -= 1
    c.save()

    resp = "SUCCESS"
    return HttpResponse(resp)


def render_review_text(request):
    # output = profanity_filter(request.POST.get("text", ""))
    output = request.POST.get("content", "")
    if output:
        review = Review(
            title=request.POST.get("title", "Untitled Review"),
            content=request.POST.get("content", ""),
            rating=float(request.POST.get("rating", -1)),
            author=request.POST.get("author", "Anonymous"),
        )
        if request.user.is_authenticated:
            review.user_id = request.user.id
            review.author = request.user.username
        output = model_block({"request": request}, review, view="review_content", hide_actions=True)
    return HttpResponse(output)


def submit_form(request, slug):
    available_forms = {
        "Collection_Content_Form": Collection_Content_Form,
        "Collection_Form": Collection_Form,
    }

    form_name = slug.replace("-", "_").title()
    form = available_forms.get(form_name)

    if not form:
        return JsonResponse({"success": False, "errors": [{"message": "Form not found"}]})

    form = form(request.POST)
    form.set_request(request)

    if form.is_valid():
        form.process()
    else:
        return JsonResponse(form.response_failure())

    return JsonResponse(form.response_success())


def update_collection_entry(request):
    if not request.POST.get("collection_id"):
        return HttpResponse("")
    # Confirm this is your collection
    c = Collection.objects.get(pk=int(request.POST["collection_id"]))
    if not request.user:
        return HttpResponse("ERROR: Unauthorized user!")
    if request.user and request.user.id != c.user.id:
        return HttpResponse("ERROR: Unauthorized user!")

    pk = int(request.POST.get("entry_id"))

    entry = Collection_Entry.objects.get(pk=pk)
    entry.collection_description = request.POST.get("desc", "")
    entry.save()

    # Check if this is the new preview image
    if request.POST.get("set_preview") == "true":
        entry.collection.preview_image = entry.zfile
        entry.collection.save()

    resp = "SUCCESS"
    return HttpResponse(resp)


def wozzt_queue_add(request):
    resp = "SUCCESS"
    e = WoZZT_Queue()

    if not request.POST or not request.user.is_staff:
        return HttpResponse("")

    # Create queue object
    try:
        d = request.POST
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
    image = open_base64_image(request.POST["b64img"])
    filepath = os.path.join(STATIC_PATH, "wozzt-queue", e.uuid + ".png")
    image.save(filepath)
    e.save()

    return HttpResponse(resp)


def get_stream_entries(request):
    if request.GET.get("pk"):
        qs = Stream_Entry.objects.filter(pk=request.GET["pk"])
    else:
        qs = Stream_Entry.objects.all().order_by("-id")[:10]

    output = {"items": []}

    for item in qs:
        output["items"].append(item.as_json())
    return JsonResponse(output)


def fetch_zip_info(request):
    """ For new file viewer"""
    path = request.GET.get("path")
    if path is None:
        return HttpResponse("No path specified")

    if "?" in path:
        path = path[:path.find("?")]
    print("OG PATH", path)
    zf_path = os.path.join(SITE_ROOT, path)
    print("SR?", SITE_ROOT)
    print("LOOKING FOR", zf_path)
    zf = zipfile.ZipFile(zf_path)
    output = {"items": []}

    for zi in zf.infolist():
        output["items"].append({"filename": zi.filename, "date_time": zipinfo_datetime_tuple_to_str(zi), "compress_type": zi.compress_type, "dir": zi.is_dir(), "crc32": zi.CRC, "compressed": zi.compress_size, "file_size": zi.file_size})
    return JsonResponse(output)


def fetch_zip_content(request):
    """ For new file viewer"""
    path = request.GET.get("path")
    if path is None:
        return HttpResponse("No path specified")

    if "?" in path:
        path = path[:path.find("?")]

    zf_path = os.path.join(SITE_ROOT, path)
    content = request.GET.get("content")

    print(zf_path, content)

    zf = zipfile.ZipFile(zf_path)
    output = {}

    fh = zf.open(content)

    response = HttpResponse(content_type="application/octet-stream")
    response["Content-Disposition"] = "attachment; filename={}".format(os.path.basename(content))
    response.write(fh.read())
    return response

def qad_get_stream_schedule(request):
    utc_timestamp = datetime.now(UTC)
    qs = Stream.objects.filter(when__gt=utc_timestamp).order_by("when")
    output = {"items": []}
    for s in qs:
        output["items"].append({"title": s.title, "preview_image": s.preview_image, "when": s.when, "description": s.description})
    return JsonResponse(output)
