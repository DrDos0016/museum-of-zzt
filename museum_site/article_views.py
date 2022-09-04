from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.safestring import mark_safe
from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *
from museum_site.text import CATEGORY_DESCRIPTIONS


def article_view(request, article_id, page=0, slug=""):
    """ Returns an article pulled from the database """
    page = int(page)
    data = {"id": article_id}
    data["custom_layout"] = "article"

    a = get_object_or_404(Article, pk=article_id)

    # Verify the article is readable with the permissions supplied
    if a.published == Article.REMOVED:
        return redirect("index")

    # Figure out the user's access
    access = Article.PUBLISHED  # Default

    # Check user's Patronage
    if request.user.is_authenticated:
        if request.user.profile.patronage >= UNPUBLISHED_ARTICLE_MINIMUM_PATRONAGE:
            access = Article.UNPUBLISHED
        elif request.user.profile.patronage >= UPCOMING_ARTICLE_MINIMUM_PATRONAGE:
            access = Article.UPCOMING

    # Check for generic or article specific passwords
    if request.GET.get("secret") == PASSWORD5DOLLARS:
        access = Article.UNPUBLISHED
    elif request.GET.get("secret") == PASSWORD2DOLLARS:
        access = Article.UPCOMING
    elif request.GET.get("secret") and request.GET["secret"] == a.secret:
        access = Article.UNPUBLISHED
    elif request.GET.get("secret"):  # Invalid password
        return redirect_with_querystring("article_lock", request.META["QUERY_STRING"], article_id=article_id, slug=slug)

    if a.published > access:  # Access level too low for article
        return redirect("article_lock", article_id=article_id, slug=slug)

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


def article_lock(request, article_id, slug=""):
    """ Page shown when a non-public article is attempted to be viewed """
    data = {
        "title": "Restricted Article",
    }

    article = Article.objects.get(pk=article_id)
    article.allow_comments = False
    data["article"] = article
    data["cost"] = Article.EARLY_ACCESS_PRICING.get(article.published, "ERROR! NO VALUE SET")
    data["release"] = article.publish_date
    return render(request, "museum_site/article_lock.html", data)
