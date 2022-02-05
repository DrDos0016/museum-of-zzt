from django.shortcuts import render
from .common import *
from .constants import *
from .models import *
from .forms import *


def debug(request, filename=None):
    data = {"title": "DEBUG PAGE"}
    data["ARTICLE_DEBUG"] = True
    data["TODO"] = "TODO"
    data["CROP"] = "CROP"

    set_captcha_seed(request)

    f = File.objects.get(pk=int(request.GET.get("id", 420)))
    data["file"] = f

    if request.GET.get("serve"):
        return serve_file(request.GET.get("serve"), request.GET.get("as", ""))

    print(request.session["captcha-seed"])

    if filename:
        return render(
            request, "museum_site/debug/{}.html".format(filename), data
        )
    else:
        return render(request, "museum_site/debug/debug.html", data)


def debug_advanced_search(request):
    data = {"title": "Advanced Search"}
    print("TODO: Make sure to support non-english!!")

    if len(request.GET):
        form = AdvancedSearchForm(request.GET)
        print("HACKY TIME")
        form.is_valid()
    else:
        form = AdvancedSearchForm(initial={"reviews": "any", "articles": "any", "details":[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UTILITY]})

    data["form"] = form
    data["grouped_fields"] = ["board_min", "board_max", "board_type"]

    return render(request, "museum_site/debug-advanced-search.html", data)


def debug_article(request, fname=""):
    data = {"id": 0}
    data["TODO"] = "TODO"
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

    return render(request, "museum_site/debug_colors.html", data)


