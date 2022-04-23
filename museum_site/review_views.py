from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *


def review_directory(request, author=None, page_num=1):
    """ Returns page listing all reviews """
    data = {
        "title": "Review Directory",
        "table_header": table_header(Review.table_fields),
        "available_views": Review.supported_views,
        "view": get_selected_view_format(request, Review.supported_views),
        "sort_options": get_sort_options(
            Review.sort_options, debug=request.session.get("DEBUG")
        )
    }

    # Pull reviews for page
    if author is None:
        qs = Review.objects.filter(approved=True).select_related("zfile", "user").defer("content")
    else:
        qs = Review.objects.filter(approved=True, author=author).select_related("zfile", "user").defer("content")

    if request.GET.get("sort") == "date":
        qs = qs.order_by("date")
    elif request.GET.get("sort") == "file":
        qs = qs.order_by("zfile__sort_title")
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

    data = get_pagination_data(request, data, qs)

    return render(request, "museum_site/generic-directory.html", data)
