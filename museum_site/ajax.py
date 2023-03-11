import base64
import uuid
import zipfile
import binascii
import os

from io import BytesIO

from django.http import HttpResponse, JsonResponse
from PIL import Image
from markdown_deux.templatetags import markdown_deux_tags

from museum_site.models import *
from museum_site.constants import *
from museum_site.core.misc import extract_file_key_from_url, record
from museum_site.core.palette import parse_pld
from museum_site.templatetags.site_tags import model_block
from museum_site.forms.collection_forms import Collection_Content_Form


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
        zip_file = zipfile.ZipFile(os.path.join(SITE_ROOT, "zgames", letter, zip_file))
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

    return HttpResponse("This file type is not currently supported for embedded content.", status=501)


def debug_file(request):
    if not os.path.isfile("/var/projects/DEV"):
        return HttpResponse("Not on production.")
    if request.GET.get("file"):
        fh = open(request.GET["file"], "rb")
        return HttpResponse(binascii.hexlify(fh.read()))
    else:
        return HttpResponse("No file provided.")


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


def render_review_text(request):
    # output = profanity_filter(request.POST.get("text", ""))
    output = request.POST.get("text", "")
    if output:
        output = markdown_deux_tags.markdown_filter(output)
    return HttpResponse(output)


def wozzt_queue_add(request):
    resp = "SUCCESS"
    d = request.POST
    e = WoZZT_Queue()

    if not request.POST or not request.user.is_staff:
        return HttpResponse("")

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
    filepath = os.path.join(SITE_ROOT, "museum_site", "static", "wozzt-queue", e.uuid + ".png")

    image.save(filepath)
    e.save()

    return HttpResponse(resp)


def add_to_collection(request):
    # TODO - This should be using the actual form and .process()
    if not request.POST.get("collection_id"):
        return HttpResponse("")
    # Confirm this is your collection
    c = Collection.objects.get(pk=int(request.POST["collection_id"]))
    if not request.user:
        return HttpResponse("ERROR: Unauthorized user!")
    if request.user and request.user.id != c.user.id:
        return HttpResponse("ERROR: Unauthorized user!")

    # If a URL was provided, convert that to an ID
    if request.POST.get("url"):
        url = request.POST.get("url")

        if not url.startswith(HOST):
            return HttpResponse("ERROR: Invalid url provided. Expecting - https://museumofzzt.com/file/&lt;action&gt;/&lt;key&gt;/")
        else:
            key = extract_file_key_from_url(url)
            if key is None:
                return HttpResponse("ERROR: Could not determine file key. Expecting - https://museumofzzt.com/file/&lt;action&gt;/&lt;key&gt;/")
            zfile_id = File.objects.get(key=key).pk
    else:
        zfile_id = request.POST["zfile_id"]

    # Check for duplicates
    duplicate = Collection_Entry.objects.duplicate_check(request.POST["collection_id"], zfile_id)

    if duplicate:
        return HttpResponse("ERROR: ZFile already exists in collection!")

    # Update collection item count
    c.item_count += 1

    entry = Collection_Entry(
        collection_id=int(request.POST["collection_id"]),
        zfile_id=int(zfile_id),
        collection_description=request.POST["collection_description"],
        order=c.item_count
    )

    # Save the collection entry
    entry.save()

    # Set the preview image if one isn't set yet
    if c.preview_image is None:
        c.preview_image = entry.zfile

    # Save the collection
    c.save()

    resp = "SUCCESS"
    return HttpResponse(resp)


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
        zfile_id=int(request.POST["zfile_id"]),
    )

    entry.delete()
    # Update count
    c.item_count -= 1
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
        entry.order = order.index(str(entry.zfile.pk)) + 1
        entry.save()

    resp = "SUCCESS"
    return HttpResponse(resp)


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
    if request.POST.get("set_preview"):
        entry.collection.preview_image = entry.zfile
        entry.collection.save()

    resp = "SUCCESS"
    return HttpResponse(resp)


def otf_get_available_collections(request):
    output = {"collections": []}
    if not request.user:
        return JsonResponse(output)
    if request.user and not request.user.id:
        return JsonResponse(output)

    qs = Collection.objects.filter(user_id=request.user.id).only("pk", "title", "visibility").order_by("title")
    for c in qs:
        output["collections"].append({"pk": c.pk, "title": c.title, "visibility": c.visibility_str[:3]})

    return JsonResponse(output)


def submit_form(request, slug):
    available_forms = {
        "Collection_Content_Form": Collection_Content_Form,
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
        return JsonResponse({"success": False, "errors": form.errors.get_json_data()["__all__"]})

    return JsonResponse({"success": True})
