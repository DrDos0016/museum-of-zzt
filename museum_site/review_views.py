from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .common import *
from .constants import *
from .models import *


def review_directory(request, page_num=1):
    """ Returns page listing all reviews """
    data = {"title": "Review Directory"}

    # Pull reviews for page
    qs = Review.objects.all().defer("content")

    if request.GET.get("sort") == "date":
        qs = qs.order_by("date")
    elif request.GET.get("sort") == "file":
        qs = qs.order_by("file__sort_title")
    elif request.GET.get("sort") == "reviewer":
        qs = qs.order_by("author")
    elif request.GET.get("sort") == "rating":
        qs = qs.order_by("-rating")
    elif request.GET.get("sort") == "id":
        qs = qs.order_by("id")
    elif request.GET.get("sort") == "-id":
        qs = qs.order_by("-id")
    else:  # Default (newest)
        qs = qs.order_by("-date")

    data["available_views"] = ["detailed", "list", "gallery"]
    data["view"] = get_selected_view_format(request, data["available_views"])
    data = get_pagination_data(request, data, qs)
    data["sort_options"] = [
        {"text": "Newest", "val": "-date"},
        {"text": "Oldest", "val": "date"},
        {"text": "File", "val": "file"},
        {"text": "Reviewer", "val": "reviewer"},
        {"text": "Rating", "val": "rating"},
    ]
    if request.session.get("DEBUG"):
        data["sort_options"] += [
            {"text": "!ID New", "val": "-id"},
            {"text": "!ID Old", "val": "id"}
        ]

    return render(request, "museum_site/review_directory.html", data)
