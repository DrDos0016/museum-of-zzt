from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .common import *
from .constants import *
from .models import *


def advanced_search(request):
    """ Returns page containing multiple filters to use when searching """
    data = {
        "title": "Advanced Search",
        "mode": "search",
        "genres": GENRE_LIST,
        "years": [str(x) for x in range(1991, YEAR + 1)]
    }

    data["details_list"] = request.GET.getlist("details", ADV_SEARCH_DEFAULTS)
    return render(request, "museum_site/advanced_search.html", data)


def article_search(request):
    """ Returns page containing multiple filters to use when searching """
    data = {
        "title": "Article Search",
        "years": [str(x) for x in range(YEAR, 1990, -1)]
    }

    data["sort_options"] = [
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
        {"text": "Category", "val": "category"},
        {"text": "Date", "val": "date"},
    ]

    data["categories"] = Article.objects.filter(
        published=PUBLISHED_ARTICLE
    ).only("category").distinct().order_by("category").values_list(
        "category", flat=True
    )

    return render(request, "museum_site/article_search.html", data)


@non_production
def deep_search(request):
    """ Returns page containing multiple filters to use when searching """
    # NOTE: UNIMPLEMENTED
    data = {
        "title": "Deep Search",
        "mode": "search",
        "genres": GENRE_LIST,
        "years": [str(x) for x in range(1991, YEAR + 1)]
    }

    data["details_list"] = request.GET.getlist("details", ADV_SEARCH_DEFAULTS)
    return render(request, "museum_site/deep_search.html", data)


def search(request):
    """ Searches database files. Returns the browse page filtered
        appropriately.
    """
    data = {"mode": "search", "title": "Search"}
    data["category"] = "Search Results"
    data["page"] = int(request.GET.get("page", 1))

    # Query strings
    data["qs_sans_page"] = qs_sans(request.GET, "page")
    data["qs_sans_view"] = qs_sans(request.GET, "view")
    sort = SORT_CODES[request.GET.get("sort", "title").strip()]

    # Determine the viewing method
    data["view"] = get_view_format(request)

    if request.GET.get("q"):  # Basic Search
        q = request.GET["q"].strip()

        if request.GET["q"] == "+DEBUG":
            request.session["DEBUG"] = 1
        if request.GET["q"] == "-DEBUG":
            request.session["DEBUG"] = 0

        data["q"] = request.GET["q"]
        qs = File.objects.filter(
            Q(title__icontains=q) |
            Q(aliases__alias__icontains=q) |
            Q(author__icontains=q) |
            Q(filename__icontains=q) |
            Q(company__icontains=q)
        ).exclude(details__id__in=[DETAIL_UPLOADED]).distinct()

        # Auto redirect for Italicized-Links in Closer Looks
        if request.GET.get("auto"):
            qs.order_by("id")
            params = qs_sans(request.GET, "q")
            return redirect(qs[0].file_url() + "?" + params)

        # Debug override
        if DEBUG:
            if request.GET.get("q") == "debug=blank":
                qs = File.objects.filter(screenshot="").exclude(
                    details__id__in=[DETAIL_LOST]
                )
            elif request.GET.get("q").startswith("debug="):
                ids = request.GET.get("q").split("=", maxsplit=1)[-1]
                qs = File.objects.filter(id__in=ids.split(",")).order_by("id")

        if data["view"] == "list":
            page_size = LIST_PAGE_SIZE
        else:
            page_size = PAGE_SIZE

        data["files"] = qs.order_by(
            *sort
        )[(data["page"] - 1) * page_size:data["page"] * page_size]
        data["count"] = qs.count()
        data["pages"] = int(1.0 * math.ceil(data["count"] / page_size))
        data["page_range"] = range(1, data["pages"] + 1)
        data["prev"] = max(1, data["page"] - 1)
        data["next"] = min(data["pages"], data["page"] + 1)

        if data["view"] == "gallery":
            destination = "museum_site/browse_gallery.html"
        elif data["view"] == "list":
            destination = "museum_site/browse_list.html"
        else:
            destination = "museum_site/browse.html"
    else:  # Advanced Search
        # Clean up empty params
        if request.GET.get("advanced"):
            new_qs = "?"
            for k in request.GET.keys():
                if k in ["advanced", "details"]:
                    continue
                if (
                    k == "board_type"
                    and not (
                        request.GET.get("board_min")
                        or request.GET.get("board_max")
                    )
                ):
                    continue
                if k == "min" and request.GET[k] == "0.0":
                    continue
                if k == "max" and request.GET[k] == "5.0":
                    continue
                if request.GET[k] not in ["", "Any"]:
                    new_qs += k + "=" + request.GET[k] + "&"

            details = request.GET.getlist("details")
            for d in details:
                new_qs += "details=" + d + "&"
            new_qs = new_qs[:-1]
            return redirect("/search"+new_qs)

        data["advanced_search"] = True
        qs = File.objects.all()
        if request.GET.get("title", "").strip():
            qs = qs.filter(
                title__icontains=request.GET.get("title", "").strip()
            )
        if request.GET.get("author", "").strip():
            qs = qs.filter(
                author__icontains=request.GET.get("author", "").strip()
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
                company__icontains=request.GET.get("company", "").strip()
            )
        if (request.GET.get("genre", "").strip() and
                request.GET.get("genre", "") != "Any"):
            qs = qs.filter(
                genre__icontains=request.GET.get("genre", "").strip()
            )
        if (request.GET.get("year", "").strip() and
                request.GET.get("year", "") != "Any" and
                request.GET.get("year", "") != "Unk"):
            qs = qs.filter(
                release_date__gte=request.GET.get("year", "1991") + "-01-01",
                release_date__lte=request.GET.get("year", "2091") + "-12-31"
            )
        elif (request.GET.get("year", "").strip() == "Unk"):
            qs = qs.filter(release_date=None)
        if (request.GET.get("min", "").strip() and
                float(request.GET.get("min", "")) > 0):
            qs = qs.filter(
                rating__gte=float(request.GET.get("min", "").strip())
            )
        if (request.GET.get("max", "").strip() and
                float(request.GET.get("max", "")) < 5):
            qs = qs.filter(
                rating__lte=float(request.GET.get("max", "").strip())
            )
        if (request.GET.get("board_min", "").strip() and
                int(request.GET.get("board_min", "")) >= 0 and
                request.GET.get("board_min", "") != ""):
            if (request.GET.get("board_type", "") == "playable"):
                qs = qs.filter(
                    playable_boards__gte=int(
                        request.GET.get("board_min", "").strip()
                    )
                )
            else:
                qs = qs.filter(
                    total_boards__gte=int(
                        request.GET.get("board_min", "").strip()
                    )
                )
        if (request.GET.get("board_max", "").strip() and
                int(request.GET.get("board_max", "")) <= 32767 and
                request.GET.get("board_max", "") != ""):
            if (request.GET.get("board_type", "") == "playable"):
                qs = qs.filter(
                    playable_boards__lte=int(
                        request.GET.get("board_max", "").strip()
                    )
                )
            else:
                qs = qs.filter(
                    total_boards__lte=int(
                        request.GET.get("board_max", "").strip()
                    )
                )
        if (request.GET.getlist("details")):
            qs = qs.filter(details__id__in=request.GET.getlist("details"))

        # Select distinct IDs
        qs = qs.distinct()

        # Show results
        sort = SORT_CODES[request.GET.get("sort", "title").strip()]
        if data["view"] == "list":
            data["files"] = qs.order_by(*sort)

            destination = "museum_site/browse_list.html"
        else:
            data["files"] = qs.order_by(*sort)[
                (data["page"] - 1) * PAGE_SIZE:data["page"] * PAGE_SIZE
            ]
            data["count"] = qs.count()
            data["pages"] = int(1.0 * math.ceil(data["count"] / PAGE_SIZE))
            data["page_range"] = range(1, data["pages"] + 1)
            data["prev"] = max(1, data["page"] - 1)
            data["next"] = min(data["pages"], data["page"] + 1)

            if data["view"] == "gallery":
                destination = "museum_site/browse_gallery.html"
            else:
                destination = "museum_site/browse.html"

    # Set page view cookie
    response = render(request, destination, data)
    response.set_cookie("view", data["view"], expires=datetime(3000, 12, 31))
    return response
