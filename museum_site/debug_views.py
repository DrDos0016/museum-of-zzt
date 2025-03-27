import glob
import os
import urllib.parse
import zipfile

from datetime import datetime

from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect

from museum_site.constants import *
from museum_site.core.detail_identifiers import *
from museum_site.core.file_utils import serve_file_as
from museum_site.core.model_utils import get_article_word_count
from museum_site.models import *
from museum_site.forms.debug_forms import Debug_Form_2023
from museum_site.settings import EXTERNAL_ARTICLE_PATH
from museum_site.forms.collection_forms import Collection_Form
from museum_site.views import error_403, error_404, error_500


@staff_member_required
def debug(request, filename=None):
    data = {"title": "DEBUG PAGE"}
    data["ARTICLE_DEBUG"] = True
    data["TODO"] = "TODO"  # Expected TODO usage.
    data["CROP"] = "CROP"

    if filename == "saves.html":
        return debug_saves(request)
    if filename == "debug-collection-form":
        return debug_collection_form(request)

    f = File.objects.get(pk=int(request.GET.get("id", 420)))
    s = Series.objects.get(pk=10)
    data["zfile"] = f

    test_wozzt = WoZZT_Queue.objects.filter(
        id__in=[8317, 8318]
    )

    test_reviews = Review.objects.filter(
        id__in=[1700, 1701, 1702, 1703, 100, 200, 300, 1720, 926]
    )

    test_zfiles = File.objects.filter(
        id__in=[278, 327, 420, 1271, 1662, 435, 310, 2367, 2876, 1240, 2095, 3415, 3471, 2568, 9999, 3798, 3480, 874]
    ).order_by("id")

    test_articles = Article.objects.filter(
        id__in=[830, 677, 827, 835, 425, 453, 659, 672, 683, 690]
    ).order_by("-id")

    test_series = Series.objects.filter(
        id__in=[10, 11, 12, 1]
    ).order_by("-id")

    test_collections = Collection.objects.filter(
        id__in=[9, 10, 2, 4, 1, 6]
    ).order_by("-id")

    test_collection_contents = Collection_Entry.objects.filter(collection_id=2).order_by("-id")

    data["available_views"] = ["detailed", "list", "gallery"]
    data["view"] = "detailed"

    data["wozzt"] = test_wozzt
    data["reviews"] = test_reviews
    data["zfiles"] = test_zfiles
    data["articles"] = test_articles
    data["series"] = test_series
    data["collections"] = test_collections
    data["collection_contents"] = test_collection_contents
    data["show"] = request.GET.get("show", "zfiles")
    # data["custom"] = test_custom_blocks

    # Widget Debug
    # data["checklist_items"] = File.objects.published()

    if request.GET.get("serve"):
        return serve_file_as(request.GET.get("serve"), request.GET.get("as", ""))

    print(data.get("zfile", "No zfile!"))

    if filename:
        return render(request, "museum_site/debug/{}.html".format(filename), data)
    else:
        return render(request, "museum_site/debug/debug.html", data)


@staff_member_required
def debug_article(request, fname=""):
    context = {"id": 0}
    context["TODO"] = "TODO"  # Expected TODO usage.
    context["CROP"] = "CROP"
    context["available_files"] = None

    fname = request.GET.get("file", fname)
    
    if not fname:
        context["title"] = "Select WIP Article"
        file_list = glob.glob(os.path.join(SITE_ROOT, "wip", "*"))
        context["available_files"] = []
        for filename in file_list:
            context["available_files"].append(os.path.basename(filename))
        return render(request, "museum_site/tools/wip-article-select.html", context)
    else:
        try:
            pk = int(fname)
        except ValueError:
            pk = 0

        if pk:  # Debug existing article
            article = Article.objects.get(pk=pk)
        else:  # Debug WIP article
            if not fname or fname == "<str:fname>":  # Blank/test values
                return redirect("index")

            filepath = os.path.join(SITE_ROOT, "wip", fname)
            if not os.path.isfile(filepath):
                filepath = os.path.join(EXTERNAL_ARTICLE_PATH, request.GET.get("file"))

            with open(filepath) as fh:
                article = Article.objects.get(pk=2)
                article.title = filepath
                article.category = "TEST"
                article.static_directory = fname[:-5]
                article.content = fh.read().replace(
                    "<!--Page-->", "<hr><b>PAGE BREAK</b><hr>"
                )
                article.publish_date = datetime.now()
                article.schema = request.GET.get("format", "django")
            context["file_path"] = filepath

        context["article"] = article
        context["veryspecial"] = True
        context["word_count"] = get_article_word_count(article)
        context["title"] = "[{} words] WIP {}".format(context["word_count"], fname)

        request.session["active_tool"] = "staff-article-wip"
        request.session["active_tool_template"] = "museum_site/tools/staff-article-wip.html"
    return render(request, "museum_site/tools/article-wip.html", context)


@staff_member_required
def debug_blank(request):
    context = {"title": "Blank Test Page"}
    return render(request, "museum_site/debug/debug-blank.html", context)


@staff_member_required
def debug_form_elements(request):
    context = {}

    if request.method == "POST":
        context["form"] = Debug_Form_2023(request.POST)
        f = context["form"]
        print(f.data)
    else:
        context["form"] = Debug_Form_2023()

    return render(request, "museum_site/debug/debug-form-elements.html", context)


@staff_member_required
def debug_widgets(request):
    context = {}

    if request.method == "POST":
        context["form"] = Debug_Form(request.POST)
    else:
        context["form"] = Debug_Form()

    return render(request, "museum_site/debug/debug-widget.html", context)


@staff_member_required
def debug_play(request):
    context = {}

    if request.GET:
        context["form"] = Zeta_Advanced_Form(request.GET)
    else:
        context["form"] = Zeta_Advanced_Form()

    return render(request, "museum_site/debug/debug-play.html", context)


@staff_member_required
def debug_collection_form(request):
    context = {"title": "Debug Collection Form"}

    if request.method == "POST":
        form = Collection_Form(request.POST)
        form.set_request(request)
        print("POSTING")
        if form.is_valid():
            print("VALID")
            form.process()
        else:
            print(form.errors)
    else:
        form = Collection_Form()

    context["form"] = form
    return render(request, "museum_site/debug/debug-collection-form.html", context)


@staff_member_required
def debug_attrs(request, key):
    context = {"title": "Debug Attributes"}
    zf = File.objects.get(key=key)
    context["zfile"] = zf
    return render(request, "museum_site/debug/debug-attrs.html", context)

def error_status_test(request, status_code):
    if status_code == 403:
        return error_403(request)
    elif status_code == 500:
        return error_500(request)
    else:
        return error_404(request)
