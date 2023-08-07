from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

import base64
import random
import tempfile
import zipfile

from io import BytesIO
from time import time

from PIL import Image


from museum_site.models import File, WoZZT_Queue
from museum_site.core.detail_identifiers import *
from museum_site.core.misc import HAS_ZOOKEEPER, zookeeper_init
from museum_site.constants import *


from django.http import JsonResponse

SORT_CODES = {
    "title": ["sort_title"],
    "author": ["authors__title", "sort_title"],
    "company": ["companies__title", "sort_title"],
    "id": ["id"],
    "-id": ["-id"],
    "rating": ["-rating", "sort_title"],
    "release": ["release_date", "sort_title"],
    "-release": ["-release_date", "sort_title"],
    "published": ["-publish_date", "-id"],
    "roulette": ["?"],
    "uploaded": ["-id"],
}

# Create your views here.
def worlds_of_zzt(request):
    if not HAS_ZOOKEEPER:
        return server_error_500(request)

    TEMP_DIR = tempfile.TemporaryDirectory(prefix="moz-")
    TEMP_PATH = TEMP_DIR.name

    # Timestamp
    ts = int(time())

    if request.GET.get("category") == "discord":
        entry = WoZZT_Queue.objects.filter(
            category="discord"
        ).order_by("-priority", "id").first()
        img_path = entry.image_path()
        f = entry.file
        selected = entry.zzt_file
        title = entry.board_name
        board_num = entry.board

        # Convert the image to base64
        with open(img_path, "rb") as fh:
            data = fh.read()
        b64 = base64.b64encode(data).decode("utf-8")

        # Roll the next image
        WoZZT_Queue().roll(category="discord")
        entry.delete_image()
        entry.delete()

    else:
        # Select a randomly displayable file
        f = File.objects.filter(details__in=[DETAIL_ZZT]).exclude(details__in=[DETAIL_UPLOADED, DETAIL_GFX]).order_by("?")[0]

        # Open it
        zh = zipfile.ZipFile(f.phys_path())

        # Find available ZZT worlds
        contents = zh.namelist()
        contents.sort()

        world_choices = []
        for content in contents:
            filename = content.lower()
            if filename.endswith(".zzt"):
                world_choices.append(content)

        # Select a world and extract it
        selected = random.choice(world_choices)
        zh.extract(selected, TEMP_PATH)

        # Parse the world with Zookeeper
        z = zookeeper_init(os.path.join(TEMP_PATH, selected))
        board_num = random.randint(0, len(z.boards) - 1)
        img_path = os.path.join(TEMP_PATH, str(ts))
        z.boards[board_num].screenshot(img_path, title_screen=(board_num == 0), format="RGB")
        title = z.boards[board_num].title

        # Convert the image to base64
        with open(img_path + ".png", "rb") as fh:
            data = fh.read()
        b64 = base64.b64encode(data).decode("utf-8")

        # Delete the files
        os.remove(img_path + ".png")
        os.remove(os.path.join(TEMP_PATH, selected))

    # Check if the file is playable online
    museum_link = "https://museumofzzt.com" + f.get_absolute_url()
    archive_link = "https://archive.org/details/" + f.archive_name if f.archive_name else None
    play_link = "https://museumofzzt.com" + f.play_url()

    output = {
        "status": "SUCCESS",
        "IMGPATH": img_path + ".png",
        "request_time": ts,
        "data": {
            "file": v1_api_json(f),
            "world": selected,
            "board": {"title": title, "number": board_num},
            "b64_image": b64,
            "museum_link": museum_link,
            "play_link": play_link,
            "archive_link": archive_link,
        }
    }
    return JsonResponse(output)

def get_file(request):
    output = {
        "status": "SUCCESS",
        "request_time": int(time()),
        "data": {
        }
    }

    f = File.objects.get(pk=int(request.GET["id"]))

    output["data"] = v1_api_json(f)

    return JsonResponse(output)

def get_random_file(request):
    output = {
        "status": "SUCCESS",
        "request_time": int(time()),
        "data": {
        }
    }

    f = File.objects.random_zzt_world()
    output["data"] = v1_api_json(f)

    return JsonResponse(output)

def help(request):
    data = {}
    return render(request, "museum_api/v1/help.html", data)

def search_files(request):
    output = {
        "status": "SUCCESS",
        "request_time": int(time()),
        "count": 0,
        "next_offset": int(request.GET.get("offset", 0)) + PAGE_SIZE,
        "data": {
            "results": []
        }
    }

    qs = File.objects.all()

    if request.GET.get("title", "").strip():
        qs = qs.filter(
            title__icontains=request.GET.get("title", "").strip()
        )
    if request.GET.get("author", "").strip():
        qs = qs.filter(
            authors__title__icontains=request.GET.get("author", "").strip()
        )
    if request.GET.get("filename", "").strip():
        qs = qs.filter(
            filename__icontains=request.GET.get(
                "filename", ""
            ).replace(
                ".zip", ""
            ).strip()
        )
    if request.GET.get("company", "").strip():
        qs = qs.filter(
            companies__title__icontains=request.GET.get("company", "").strip()
        )
    if (request.GET.get("genre", "").strip() and request.GET.get("genre", "").lower() != "any"):
        qs = qs.filter(genres__title__icontains=request.GET.get("genre", "").strip())
    if (request.GET.get("year", "").strip() and
            request.GET.get("year", "") != "Any" and
            request.GET.get("year", "") != "Unk"):
        qs = qs.filter(
            release_date__gte=request.GET.get("year", "1991") + "-01-01",
            release_date__lte=request.GET.get("year", "2091") + "-12-31"
        )
    elif (request.GET.get("year", "").strip() == "Unk"):
        qs = qs.filter(release_date=None)


    sort = SORT_CODES[request.GET.get("sort", "title").strip()]
    qs = qs.order_by(*sort)[int(request.GET.get("offset", 0)):int(request.GET.get("offset", 0)) + PAGE_SIZE]

    for f in qs:
        output["data"]["results"].append(v1_api_json(f))

    output["count"] = len(output["data"]["results"])

    return JsonResponse(output)

def v1_api_json(zf):
    """ Former model function to return some information in JSON format """
    data = {
        "letter": zf.letter,
        "filename": zf.filename,
        "title": zf.title,
        "sort_title": zf.sort_title,
        "author": zf.related_list("authors"),
        "size": zf.size,
        "genres": zf.genre_list(),
        "release_date": zf.release_date,
        "release_source": zf.release_source,
        "screenshot": zf.screenshot,
        "company": zf.get_related_list("companies", "title"),
        "description": zf.description,
        "review_count": zf.review_count,
        "rating": zf.rating,
        "details": [],
        "articles": [],
        "aliases": [],
        "article_count": zf.article_count,
        "checksum": zf.checksum,
        "playable_boards": zf.playable_boards,
        "total_boards": zf.total_boards,
        "archive_name": zf.archive_name,
        "publish_date": zf.publish_date,
        "last_modified": zf.last_modified,
        "explicit": int(zf.explicit),
    }

    for d in zf.details.all():
        data["details"].append({"id": d.id, "detail": d.title})

    for a in zf.articles.all().only("id", "title"):
        data["articles"].append({"id": a.id, "title": a.title})

    for a in zf.aliases.all():
        data["aliases"].append({"id": a.id, "alias": a.alias})

    return data
