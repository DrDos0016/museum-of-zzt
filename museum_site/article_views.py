from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .common import *
from .constants import *
from .models import *

from .file_views import file_articles  # Kludge


def article_categories(request, category="all", page_num=1):
    """ Returns page listing all articles sorted either by date or name """
    data = {"title": "Article Categories"}

    qs = Article.objects.not_removed().values(
        "category"
    ).annotate(total=Count("category")).order_by("category")

    data["totals"] = {}
    for entry in qs:
        key = entry["category"].split(" ")[0].lower().replace("'", "")
        data["totals"][key] = entry["total"]

    return render(request, "museum_site/article-categories.html", data)


def article_directory(request, category="all", page_num=1):
    """ Returns page listing all articles sorted either by date or name """
    data = {"title": "Article Directory"}

    # Pull articles for page
    qs = Article.objects.search(request.GET)

    if category != "all":
        if category == "lets-play":  # Special case for apostrophe
            category = "Let's Play"
        else:
            category = category.replace("-", " ")
            category = category.title()

        qs = qs.filter(category=category)
        data["title"] = category + " Directory"
        data["category"] = category

    if request.GET.get("sort") == "date":
        qs = qs.order_by("publish_date")
    elif request.GET.get("sort") == "title":
        qs = qs.order_by("title")
    elif request.GET.get("sort") == "author":
        qs = qs.order_by("author")
    elif request.GET.get("sort") == "category":
        qs = qs.order_by("category")
    elif request.GET.get("sort") == "id":
        qs = qs.order_by("id")
    elif request.GET.get("sort") == "-id":
        qs = qs.order_by("-id")
    else:  # Default (newest)
        qs = qs.order_by("-publish_date")

    data["available_views"] = ["detailed", "list", "gallery"]
    data["view"] = get_selected_view_format(request, data["available_views"])
    data = get_pagination_data(request, data, qs)
    data["sort_options"] = [
        {"text": "Newest", "val": "-date"},
        {"text": "Oldest", "val": "date"},
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
        {"text": "Category", "val": "category"},
    ]
    if request.session.get("DEBUG"):
        data["sort_options"] += [
            {"text": "!ID New", "val": "-id"},
            {"text": "!ID Old", "val": "id"}
        ]

    return render(request, "museum_site/article_directory.html", data)


def article_view(request, article_id, page=0, slug=""):
    """ Returns an article pulled from the database """
    # Awful kludge to deal with a url conflict
    if article_id == "1":
        uri = request.build_absolute_uri()
        filename = uri.split("/")[-1]
        return file_articles(request, article_id, filename)

    page = int(page)
    data = {"id": article_id}
    data["custom_layout"] = "article"
    restricted = False

    a = get_object_or_404(Article, pk=article_id)

    # Verify the article is readable with the permissions supplied
    if a.published == Article.REMOVED:
        return redirect("index")

    # Figure out the user's access
    access = Article.PUBLISHED  # Default

    # Check user's Patronage
    if request.user.is_authenticated:
        if request.user.profile.patronage >= 500:
            access = Article.UNPUBLISHED
        elif request.user.profile.patronage >= 200:
            access = Article.UPCOMING

    # Check for generic or article specific passwords
    if request.GET.get("secret") == PASSWORD5DOLLARS:
        access = Article.UNPUBLISHED
    elif request.GET.get("secret") == PASSWORD2DOLLARS:
        access = Article.UPCOMING
    elif request.GET.get("secret") and request.GET["secret"] == a.secret:
        access = Article.UNPUBLISHED
    elif request.GET.get("secret"):  # Invalid password
        return redirect("patron_articles")

    if a.published > access:  # Access level too low for article
        restricted = True
        if a.published == Article.UPCOMING:
            cost = "2"
        elif a.published == Article.UNPUBLISHED:
            cost = "5"
        release = a.publish_date.strftime("%A %B %d")
        a.content = LOCKED_ARTICLE_TEXT.replace("[COST]", cost)
        a.content = a.content.replace("[RELEASE]", release)
        a.schema = "django"

    elif a.published != Article.PUBLISHED:
        data["private_disclaimer"] = True

    # Set up pages
    data["page"] = page
    data["page_count"] = a.content.count("<!--Page-->") + 1
    data["page_range"] = list(range(1, data["page_count"] + 1))
    data["next"] = None if page + 1 > data["page_count"] else page + 1
    data["prev"] = page - 1
    data["slug"] = str(slug)

    # Set up related files
    zgames = a.file_set.all()
    if zgames:
        data["file"] = zgames[0]
        if len(zgames) > 1:
            data["multifile"] = True
            data["zgames"] = zgames

            if request.GET.get("alt_file"):
                data["file"] = get_object_or_404(
                    zgames, filename=request.GET["alt_file"]
                )

    # Split article to current page
    a.content = a.content.split("<!--Page-->")[data["page"]-1]

    data["article"] = a
    data["title"] = a.title
    return render(request, "museum_site/article_view.html", data)


def patron_articles(request):
    data = {"title": "Early Article Access"}
    upcoming = Article.objects.upcoming()
    unpublished = Article.objects.unpublished()

    data["upcoming"] = []
    data["unpublished"] = []
    data["access"] = None

    # Parse the password
    if request.POST.get("secret") == PASSWORD2DOLLARS:
        data["access"] = "upcoming"
    elif request.POST.get("secret") == PASSWORD5DOLLARS:
        data["access"] = "unpublished"
    elif request.POST.get("secret") is not None:
        data["wrong_password"] = True

    # Tweak titles and URLs for this page
    for a in upcoming:
        if data["access"] == "upcoming":
            a.url = a.url() + "?secret=" + PASSWORD2DOLLARS
        elif data["access"] == "unpublished":
            a.url = a.url() + "?secret=" + PASSWORD5DOLLARS
        data["upcoming"].append(a)

    for a in unpublished:
        if data["access"] == "unpublished":
            a.url = a.url() + "?secret=" + PASSWORD5DOLLARS
        data["unpublished"].append(a)

    return render(request, "museum_site/patreon_articles.html", data)
