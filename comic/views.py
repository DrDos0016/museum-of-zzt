import math

from django.shortcuts import render, redirect
from .models import Comic

from museum_site.constants import PAGE_SIZE


def cast(request, comic_account):
    data = {}
    return render(request, "comic/cast.html", data)


def index(request):
    data = {}
    return render(request, "comic/index.html", data)


def search(request, comic_account):
    data = {"comic_account": comic_account, "page": request.GET.get("page", 1)}
    data["q"] = request.GET.get("q")
    if data["q"]:
        data["results"] = Comic.objects.filter(
            transcript__contains=data["q"]
        )[(data["page"] - 1) * PAGE_SIZE:data["page"] * PAGE_SIZE]
        data["count"] = Comic.objects.filter(
            transcript__contains=data["q"]
        ).count()
        data["pages"] = int(math.ceil(1.0 * data["count"] / PAGE_SIZE))
        data["page_range"] = range(1, data["pages"] + 1)
        data["prev"] = max(1, data["page"] - 1)
        data["next"] = min(data["pages"], data["page"] + 1)
    return render(request, "comic/search.html", data)


def strip(request, comic_account, id=None, name=None):
    data = {"comic_account": comic_account}
    if id is None:
        # TODO: This is terrible.
        FIRST_COMIC = {"bencomic": 1, "lemmy": 878, "mr-shapiro": 967, "nomad": 971, "kaddar": 981, "revvy": 988, "zamros": 994, "frost": 1015, "ubgs": 1053}
        id = FIRST_COMIC[comic_account]
    data["comic"] = Comic.objects.get(comic_account=comic_account, pk=id)
    data["prev"] = Comic.objects.filter(comic_account=comic_account, pk__lt=id).order_by("-id")
    data["next"] = Comic.objects.filter(comic_account=comic_account, pk__gt=id).order_by("id")
    data["comic_list"] = Comic.objects.only("id", "title", "date").filter(comic_account=comic_account)

    if comic_account in ["bencomic", "benco"]:
        return redirect("/")
    else:
        return render(request, "comic/strip.html", data)
