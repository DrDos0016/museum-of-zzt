from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .common import *
from .constants import *
from .models import *


def series_directory(request, page_num=1):
    """ Returns a directory of all series in the database """
    data = {
        "title": "Series Directory",
    }

    qs = Series.objects.search(request.GET)

    if request.GET.get("sort") == "title":
        qs = qs.order_by("title")
    elif request.GET.get("sort") == "id":
        qs = qs.order_by("id")
    elif request.GET.get("sort") == "-id":
        qs = qs.order_by("-id")
    else:  # Default (Latest entry)
        qs = qs.order_by("-last_entry_date", "title")

    data["available_views"] = ["detailed", "list", "gallery"]
    data["view"] = get_selected_view_format(request, data["available_views"])
    data = get_pagination_data(request, data, qs)
    data["sort_options"] = [
        {"text": "Newest Entry", "val": "latest"},
        {"text": "Title", "val": "title"},
    ]
    if request.session.get("DEBUG"):
        data["sort_options"] += [
            {"text": "!ID New", "val": "-id"},
            {"text": "!ID Old", "val": "id"}
        ]

    return render(request, "museum_site/series-directory.html", data)


def series_overview(request, series_id, slug=""):
    data = {
        "title": "Series Overview"
    }

    series = Series.objects.filter(pk=series_id, visible=True).first()
    data["series"] = series
    data["articles"] = series.article_set.all().order_by("publish_date")

    return render(request, "museum_site/series-view.html", data)
