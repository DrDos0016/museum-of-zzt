from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .common import *
from .constants import *
from .models import *

from .file_views import file_articles  # Kludge


def article_directory(request, category="all", page_num=1):
    """ Returns page listing all articles sorted either by date or name """
    data = {"title": "Article Directory"}

    # Pull articles for page
    qs = Article.search(request.GET)

    if category != "all":
        qs = qs.filter(category=category)
        data["title"] = category.title() + " Directory"
        data["category"] = category.title()

    if request.GET.get("sort", "date") == "date":
        qs = qs.order_by("-date")
    elif request.GET.get("sort") == "title":
        qs = qs.order_by("title")
    elif request.GET.get("sort") == "author":
        qs = qs.order_by("author")
    elif request.GET.get("sort") == "category":
        qs = qs.order_by("category")

    data["available_views"] = ["detailed", "list", "gallery"]
    data["view"] = get_selected_view_format(request, data["available_views"])
    data = get_pagination_data(request, data, qs)
    data["sort_options"] = [
        {"text": "Date", "val": "date"},
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
        {"text": "Category", "val": "category"},
    ]

    return render(request, "museum_site/article_directory.html", data)


def article_view(request, article_id, page=0):
    """ Returns an article pulled from the database """
    # Awful kludge to deal with a url conflict
    if article_id == "1":
        uri = request.build_absolute_uri()
        filename = uri.split("/")[-1]
        return file_articles(request, article_id, filename)

    slug = request.path.split("/")[-1]
    page = int(page)
    data = {"id": article_id}
    data["custom_layout"] = "article"

    if request.GET.get("secret") is None:
        data["article"] = get_object_or_404(
            Article, pk=article_id, published=PUBLISHED_ARTICLE
        )
    elif request.GET.get("secret") == PASSWORD2DOLLARS:
        data["access"] = "early"
        data["article"] = get_object_or_404(
            Article,
            Q(published=PUBLISHED_ARTICLE) | Q(published=UPCOMING_ARTICLE),
            pk=article_id
        )
        data["private_disclaimer"] = True

    elif request.GET.get("secret") == PASSWORD5DOLLARS:
        data["access"] = "really_early"
        data["article"] = get_object_or_404(
            Article,
            Q(published=PUBLISHED_ARTICLE) |
            Q(published=UPCOMING_ARTICLE) |
            Q(published=UNPUBLISHED_ARTICLE),
            pk=article_id,
        )
        data["private_disclaimer"] = True
    data["page"] = page
    data["page_count"] = data["article"].content.count("<!--Page-->") + 1
    data["page_range"] = list(range(1, data["page_count"] + 1))
    data["next"] = None if page + 1 > data["page_count"] else page + 1
    data["prev"] = page - 1
    data["slug"] = str(slug)

    data["title"] = data["article"].title

    zgames = data["article"].file_set.all()
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
    data["article"].content = data["article"].content.split(
        "<!--Page-->"
    )[data["page"]-1]
    return render(request, "museum_site/article_view.html", data)


def patron_articles(request):
    data = {}
    data["early"] = Article.objects.filter(published=UPCOMING_ARTICLE)
    data["really_early"] = Article.objects.filter(published=UNPUBLISHED_ARTICLE)

    if request.POST.get("secret") == PASSWORD2DOLLARS:
        data["access"] = "early"
    elif request.POST.get("secret") == PASSWORD5DOLLARS:
        data["access"] = "really_early"
    elif request.POST.get("secret") is not None:
        data["wrong_password"] = True

    return render(request, "museum_site/patreon_articles.html", data)
