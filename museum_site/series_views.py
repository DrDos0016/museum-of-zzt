from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *


def series_directory(request, page_num=1):
    """ Returns a directory of all series in the database """
    data = {
        "title": "Series Directory",
        "table_header": table_header(Series.table_fields),
        "available_views": Series.supported_views,
        "view":get_selected_view_format(request, Series.supported_views),
        "sort_options": get_sort_options(
            Series.sort_options, debug=request.session.get("DEBUG")
        )
    }

    qs = Series.objects.search(request.GET)

    if request.GET.get("sort") == "title":
        qs = qs.order_by("title")
    elif request.GET.get("sort") == "id":
        qs = qs.order_by("id")
    elif request.GET.get("sort") == "-id":
        qs = qs.order_by("-id")
    else:  # Default (Newest entry)
        qs = qs.order_by("-last_entry_date", "title")

    data = get_pagination_data(request, data, qs)

    return render(request, "museum_site/generic-directory.html", data)


def series_overview(request, series_id, slug=""):
    data = {
        "title": "Series Overview",
    }

    series = Series.objects.filter(pk=series_id, visible=True).first()
    data["series"] = series
    data["articles"] = series.article_set.all().order_by("publish_date")

    return render(request, "museum_site/series-view.html", data)
