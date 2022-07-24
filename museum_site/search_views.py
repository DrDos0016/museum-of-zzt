from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.generic.edit import FormView
from museum_site.common import *
from museum_site.constants import *
from museum_site.core.detail_identifiers import *
from museum_site.forms import *
from museum_site.models import *

ADV_SEARCH_DEFAULTS = [
    DETAIL_ZZT,
    DETAIL_SZZT,
    DETAIL_UTILITY,
]


def advanced_search(request):
    """ Returns page containing multiple filters to use when searching """
    data = {"title": "Advanced Search"}

    if request.GET:
        form = Advanced_Search_Form(request.GET)

        if request.GET.get("action") != "edit" and form.is_valid():
            return redirect_with_querystring("search", request.GET.urlencode())
    else:
        form = Advanced_Search_Form(initial={"details":[DETAIL_ZZT, DETAIL_SZZT, DETAIL_WEAVE, DETAIL_UPLOADED]})

    data["form"] = form
    return render(request, "museum_site/advanced-search.html", data)

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
