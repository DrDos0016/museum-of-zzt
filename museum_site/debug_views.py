from django.shortcuts import render
from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *
from museum_site.forms import *


def debug(request, filename=None):
    data = {"title": "DEBUG PAGE"}
    data["ARTICLE_DEBUG"] = True
    data["TODO"] = "TODO"  # Expected TODO usage.
    data["CROP"] = "CROP"

    if filename == "saves.html":
        return debug_saves(request)

    f = File.objects.get(pk=int(request.GET.get("id", 420)))
    s = Series.objects.get(pk=10)

    test_wozzt = WoZZT_Queue.objects.filter(
        id__in=[5155, 5156, 5157, 5158]
    )

    test_reviews = Review.objects.filter(
        id__in=[1700, 1701, 1702, 1703, 100, 200, 300, 1720]
    )

    test_zfiles = File.objects.filter(
        id__in=[327, 420, 1271, 1662, 435, 310, 2367, 2876, 1240, 2095, 3415, 3471]
    ).order_by("id")

    test_articles = Article.objects.filter(
        id__in=[425, 453, 659, 672, 683, 690]
    ).order_by("-id")

    test_series = Series.objects.filter(
        id__in=[10, 11, 12, 1]
    ).order_by("-id")

    data["available_views"] = ["detailed", "list", "gallery"]
    data["view"] = get_selected_view_format(request, data["available_views"])

    #data["wozzt_table_header"] = table_header(test_wozzt[0].table_fields)
    #data["review_table_header"] = table_header(test_reviews[0].table_fields)
    #data["zfile_table_header"] = table_header(test_zfiles[0].table_fields)
    #data["article_table_header"] = table_header(test_articles[0].table_fields)
    #data["series_table_header"] = table_header(test_series[0].table_fields)

    data["wozzt"] = test_wozzt
    data["reviews"] = test_reviews
    data["zfiles"] = test_zfiles
    data["articles"] = test_articles
    data["series"] = test_series

    if request.GET.get("serve"):
        return serve_file(request.GET.get("serve"), request.GET.get("as", ""))

    if filename:
        return render(
            request, "museum_site/debug/{}.html".format(filename), data
        )
    else:
        return render(request, "museum_site/debug/debug.html", data)


def debug_advanced_search(request):
    data = {"title": "Advanced Search"}
    record("TODO: Make sure to support non-english!!")

    if len(request.GET):
        form = AdvancedSearchForm(request.GET)
        record("HACKY TIME")
        form.is_valid()
    else:
        form = AdvancedSearchForm(initial={"reviews": "any", "articles": "any", "details":[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UTILITY]})

    data["form"] = form
    data["grouped_fields"] = ["board_min", "board_max", "board_type"]

    return render(request, "museum_site/debug/debug-advanced-search.html", data)


def debug_article(request, fname=""):
    data = {"id": 0}
    data["TODO"] = "TODO"  # Expected TODO usage.
    data["CROP"] = "CROP"

    fname = request.GET.get("file", fname)

    if not fname or fname == "<str:fname>":  # Blank/test values
        return redirect("index")

    filepath = os.path.join(SITE_ROOT, "wip", fname)
    if not os.path.isfile(filepath):
        filepath = "/media/drdos/Thumb16/projects/" + request.GET.get("file")

    with open(filepath) as fh:
        article = Article.objects.get(pk=2)
        article.title = filepath
        article.category = "TEST"
        article.static_directory = "wip-" + fname[:-5]
        article.content = fh.read().replace(
            "<!--Page-->", "<hr><b>PAGE BREAK</b><hr>"
        )
        article.schema = request.GET.get("format", "django")
    data["article"] = article
    data["veryspecial"] = True
    data["file_path"] = filepath
    return render(request, "museum_site/article_view.html", data)


def debug_colors(request):
    data = {"title": "DEBUG COLORS", "stylesheets": {}}

    for stylesheet in CSS_INCLUDES:
        data["stylesheets"][stylesheet] = []
        data["solarized"] = [
            "#002B36", "#073642", "#586E75", "#657B83",
            "#839496", "#93A1A1", "#EEE8D5", "#FDF6E3",
            "#B58900", "#CB4B16", "#DC322F", "#D33682",
            "#6C71C4", "#268BD2", "#2AA198", "#859900",
        ]
        data["ega"] = [
            "#000", "#00A", "#0A0", "#0AA",
            "#A00", "#A0A", "#A50", "#AAA",
            "#555", "#55F", "#5F5", "#5FF",
            "#F55", "#F5F", "#FF5", "#FFF",
        ]
        path = os.path.join(STATIC_PATH, "css", stylesheet)
        with open(path) as fh:
            for line in fh.readlines():
                matches = re.findall("#(?:[0-9a-fA-F]{3}){1,2}", line)
                for m in matches:
                    if m not in data["stylesheets"][stylesheet]:
                        data["stylesheets"][stylesheet].append(m)

            data["stylesheets"][stylesheet].sort()

    return render(request, "museum_site/debug/debug_colors.html", data)
