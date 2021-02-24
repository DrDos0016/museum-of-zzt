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

    if request.GET.get("sort", "date") == "date":
        qs = qs.order_by("-date")
    elif request.GET.get("sort") == "file":
        qs = qs.order_by("file__sort_title")
    elif request.GET.get("sort") == "reviewer":
        qs = qs.order_by("author")
    elif request.GET.get("sort") == "rating":
        qs = qs.order_by("-rating")


    data["available_views"] = ["detailed", "list", "gallery"]
    data["view"] = get_selected_view_format(request, data["available_views"])
    data = get_pagination_data(request, data, qs)
    data["sort_options"] = [
        {"text": "Date", "val": "date"},
        {"text": "File", "val": "file"},
        {"text": "Reviewer", "val": "reviewer"},
        {"text": "Rating", "val": "rating"},
    ]

    return render(request, "museum_site/review_directory.html", data)
