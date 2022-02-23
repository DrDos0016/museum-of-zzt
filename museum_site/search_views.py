from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .common import *
from .constants import *
from .forms import ArticleSearchForm
from .models import *

ADV_SEARCH_DEFAULTS = [
    DETAIL_ZZT,
    DETAIL_SZZT,
    DETAIL_UTILITY,
]


def advanced_search(request):
    """ Returns page containing multiple filters to use when searching """
    data = {
        "title": "Advanced Search",
        "mode": "search",
        "genres": GENRE_LIST,
        "years": [str(x) for x in range(1991, YEAR + 1)]
    }

    data["details_list"] = request.GET.getlist("details", ADV_SEARCH_DEFAULTS)
    data["details_list"] = list(map(int, data["details_list"]))
    data["detail_cats"] = Detail.objects.advanced_search_categories()
    data["languages"] = LANGUAGE_CHOICES

    return render(request, "museum_site/advanced_search.html", data)


def article_search(request):
    """ Returns page containing multiple filters to use when searching """
    data = {
        "title": "Article Search",
    }

    if request.GET:
        form = ArticleSearchForm(request.GET)
    else:
        form = ArticleSearchForm()

    if request.session.get("DEBUG"):
        form.fields["sort"].choices += [
            ("-id", "!ID New"),
            ("id", "!ID Old"),
        ]

    data["form"] = form

    return render(request, "museum_site/article_search.html", data)
