from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.generic import DetailView
from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *


class Article_Detail_View(DetailView):
    model = Article
    template_name = "museum_site/article_view.html"

    def setup(self, request, *args, **kwargs):
        self.slug = kwargs.get("slug")
        self.article_id = kwargs.get("pk")
        if "slug" in kwargs.keys():
            del kwargs["slug"]
        super().setup(request, *args, **kwargs)

    def get_user_access_level(self):
        access = Article.PUBLISHED  # Default access level
        if self.request.user.is_authenticated:  # Check for patronage based access level
            if self.request.user.profile.patronage >= UNPUBLISHED_ARTICLE_MINIMUM_PATRONAGE:
                access = Article.UNPUBLISHED
            elif self.request.user.profile.patronage >= UPCOMING_ARTICLE_MINIMUM_PATRONAGE:
                access = Article.UPCOMING

        # Check for generic or article specific passwords
        if self.request.GET.get("secret") in [PASSWORD5DOLLARS, self.object.secret]:
            access = Article.UNPUBLISHED
        elif self.request.GET.get("secret") == PASSWORD2DOLLARS:
            access = Article.UPCOMING
        return access

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.object.title
        context["slug"] = self.slug
        context["private_disclaimer"] = (self.object.published != Article.PUBLISHED)

        # Set up related files
        zgames = self.object.file_set.all()
        if zgames:
            context["file"] = zgames[0] if not self.request.GET.get("alt_file") else get_object_or_404(zgames, filename=self.request.GET["alt_file"])
            context["zgames"] = zgames

        # Set up pagination
        context["page"] = self.kwargs.get("page", 1)
        context["page_count"] = self.object.content.count("<!--Page-->") + 1
        context["page_range"] = list(range(1, context["page_count"] + 1))
        context["next"] = None if context["page"] + 1 > context["page_count"] else context["page"] + 1
        context["prev"] = context["page"] - 1
        context["article"].content = self.object.content.split("<!--Page-->")[context["page"]-1]

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.object.published > self.get_user_access_level():  # Access level too low for article
            return redirect_with_querystring("article_lock", self.request.META["QUERY_STRING"], article_id=self.object.pk, slug=self.slug)
        if self.object.published == Article.REMOVED:  # Block requests for REMOVED articles
            raise PermissionDenied()
        return super().render_to_response(context, **response_kwargs)


def patron_articles(request):
    data = {"title": "Early Article Access", "upcoming": Article.objects.upcoming(), "unpublished": Article.objects.unpublished()}
    return render(request, "museum_site/patreon_articles.html", data)


def article_lock(request, article_id, slug=""):
    """ Page shown when a non-public article is attempted to be viewed """
    article = Article.objects.get(pk=article_id)
    article.allow_comments = False
    data = {"title": "Restricted Article", "article": article, "cost": article.early_access_price, "release": article.publish_date}
    return render(request, "museum_site/article_lock.html", data)
