from django.shortcuts import render
from .common import *
from .constants import *

def debug(request):
    data = {"title": "DEBUG PAGE"}

    #results = File.objects.filter(Q(author="Dr. Dos") | Q(review))
    #print("Found", len(results), "by me")
    #data["results"] = results

    set_captcha_seed(request)

    f = File.objects.filter(pk=int(request.GET.get("id", 420)))
    data["file"] = f



    print(request.session["captcha-seed"])

    return render(request, "museum_site/debug.html", data)


def debug_article(request):
    data = {"id": 0}
    filepath = "/var/projects/museum/private/" + request.GET.get("file")
    if not os.path.isfile(filepath):
        filepath = "/media/drdos/Thumb16/projects/" + request.GET.get("file")

    with open(filepath) as fh:
        article = Article.objects.get(pk=1)
        article.title = "TEST ARTICLE"
        article.category = "TEST"
        article.content = fh.read().replace("<!--Page-->", "<hr><b>PAGE BREAK</b><hr>")
        article.schema = request.GET.get("format", "django")
    data["article"] = article
    data["veryspecial"] = True
    return render(request, "museum_site/article_view.html", data)


def debug_colors(request):
    data = {"title": "DEBUG COLORS", "stylesheets":{}}

    for stylesheet in CSS_INCLUDES:
        data["stylesheets"][stylesheet] = []
        path = os.path.join(STATIC_PATH, "css", stylesheet)
        print("PATH", path)
        with open(path) as fh:
            for line in fh.readlines():
                matches = re.findall(".*#[aA-Ff0-9][aA-Ff0-9][aA-Ff0-9]", line)
                for m in matches:
                    data["stylesheets"][stylesheet].append(m[m.rfind("#"):])
                matches = re.findall(".*#[aA-Ff0-9][aA-Ff0-9][aA-Ff0-9][aA-Ff0-9][aA-Ff0-9][aA-Ff0-9]", line)
                for m in matches:
                    data["stylesheets"][stylesheet].append(m[m.rfind("#"):])

            data["stylesheets"][stylesheet].sort()

    return render(request, "museum_site/debug_colors.html", data)

def debug_z0x(request):
    data = {}
    return render(request, "museum_site/z0x.html", data)
