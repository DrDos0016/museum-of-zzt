from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.safestring import mark_safe
from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *
from museum_site.text import CATEGORY_DESCRIPTIONS

from museum_site.file_views import file_articles  # Kludge


def article_categories(request, category="all", page_num=1):
    """ Returns page listing all articles sorted either by date or name """
    data = {"title": "Article Categories"}

    qs = Article.objects.not_removed().values(
        "category"
    ).annotate(total=Count("category")).order_by("category")

    # TODO: Sloppy way to get this information
    seen_categories = []
    cats = {}
    cats_qs = Article.objects.published().defer("content").order_by("-id")
    for a in cats_qs:
        if a.category not in seen_categories:
            seen_categories.append(a.category)
            cats[a.category.lower()] = a

    # Block
    data["page"] = []

    for entry in qs:
        key = entry["category"].lower().replace("'", "").replace(" ", "-")
        latest = cats[entry["category"].lower()]
        block_context = dict(
            pk=None,
            model=None,
            preview=dict(url="/static/pages/article-categories/{}.png".format(
                key
            ), alt=entry["category"]),
            title={"datum": "link", "url": "/article/"+key, "value": entry["category"]},
            columns=[[
                    {"datum": "text", "label": "Number of Articles", "value":entry["total"]},
                    {"datum": "link", "label": "Latest", "url": latest.url(), "value": latest.title},
                    {
                        "datum": "text",
                        "value":mark_safe(CATEGORY_DESCRIPTIONS.get(key, "<i>No description available</i>"))
                    }
            ]],
        )

        data["page"].append(block_context)

    return render(request, "museum_site/generic-directory.html", data)


def article_directory(request, category="all", page_num=1):
    """ Returns page listing all/a category of articles """
    data = {
        "title": "Article Directory",
        "table_header": table_header(Article.table_fields),
        "available_views": Article.supported_views,
        "view": get_selected_view_format(request, Article.supported_views),
        "sort_options": get_sort_options(
            Article.sort_options, debug=request.session.get("DEBUG")
        ),
        "model": "Article",
        "sort": request.GET.get("sort"),
    }

    prefix_templates = {
        "closer-look": "museum_site/prefixes/closer-look.html",
        "livestream": "museum_site/prefixes/livestream.html",
        "publication-pack": "museum_site/prefixes/publication-pack.html",
    }
    if prefix_templates.get(category):
        data["prefix_template"] = prefix_templates[category]

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

    data = get_pagination_data(request, data, qs)

    if data["page"].object_list:
        data["first_item"] = data["page"].object_list[0]
        data["last_item"] = (
            data["page"].object_list[len(data["page"].object_list) - 1]
        )

    return render(request, "museum_site/generic-directory.html", data)


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

    data["upcoming"] = upcoming
    data["unpublished"] = unpublished
    data["access"] = None

    # Parse the password
    if request.POST.get("secret") == PASSWORD2DOLLARS:
        data["access"] = "upcoming"
        password_qs = "?secret=" + PASSWORD2DOLLARS
    elif request.POST.get("secret") == PASSWORD5DOLLARS:
        data["access"] = "unpublished"
        password_qs = "?secret=" + PASSWORD5DOLLARS
    elif request.POST.get("secret") is not None:
        data["wrong_password"] = True
        password_qs = ""

    # Tweak titles and URLs for this page
    for a in upcoming:
        if data["access"] in ["upcoming", "unpublished"]:
            a.extra_context = {"password_qs": password_qs}

    for a in unpublished:
        if data["access"] == "unpublished":
            a.extra_context = {"password_qs": password_qs}

    return render(request, "museum_site/patreon_articles.html", data)
