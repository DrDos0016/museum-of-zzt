import math

from django.shortcuts import render
from .models import Comic

# Use main site's page size if availalbe
try:
    from z2_site.common import PAGE_SIZE
except ImportError:
    PAGE_SIZE = 25  # Fallback

def cast(request):
    data = {}
    return render(request, "bencomic/cast.html", data)


def index(request, id=None):
    data = {}
    if id is None:
        id = 1
        data["intro"] = True
    data["comic"] = Comic.objects.get(pk=id)
    data["prev"] = Comic.objects.filter(pk__lt=id).order_by("-id")
    data["next"] = Comic.objects.filter(pk__gt=id).order_by("id")
    data["comic_list"] = Comic.objects.only("id", "title", "date").all()
    return render(request, "bencomic/index.html", data)


def search(request):
    data = {"page": request.GET.get("page", 1)}
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
    return render(request, "bencomic/search.html", data)
