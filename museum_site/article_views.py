from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from museum_site.constants import *
from museum_site.core.redirects import redirect_with_querystring
from museum_site.forms.article_forms import Article_Search_Form
from museum_site.models import *


class Article_Detail_View(DetailView):
    model = Article
    template_name = "museum_site/article-view.html"

    def setup(self, request, *args, **kwargs):
        self.slug = kwargs.get("slug")
        self.article_id = kwargs.get("pk")
        if "slug" in kwargs.keys():
            del kwargs["slug"]
        super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.init_model_block_context("detailed", request=self.request)
        context["title"] = self.object.title
        context["slug"] = self.slug
        context["private_disclaimer"] = (self.object.published != Article.PUBLISHED)

        # Set up related files
        zgames = self.object.file_set.all()
        if zgames:
            context["file"] = zgames[0] if not self.request.GET.get("alt_file") else get_object_or_404(zgames, key=self.request.GET["alt_file"])
            context["zgames"] = zgames

        # Set up pagination
        context["page"] = self.kwargs.get("page", 1)
        context["page_count"] = self.object.content.count("<!--Page-->") + 1
        context["page_range"] = list(range(1, context["page_count"] + 1))
        context["next"] = None if context["page"] + 1 > context["page_count"] else context["page"] + 1
        context["prev"] = context["page"] - 1
        context["article"].content = self.object.content.split("<!--Page-->")[context["page"]-1]
        if "<!--Page-->" in context["article"].footnotes:  # Only split if there are mutiple pages that need footnotes
            context["article"].footnotes = self.object.footnotes.split("<!--Page-->")[context["page"]-1]
        elif context["page"] > 1:  # Otherwise hide the footnotes on all but the first page
            context["article"].footnotes = ""

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.object.published > self.object.user_access_level:  # Access level too low for article
            return redirect_with_querystring("article_lock", self.request.META["QUERY_STRING"], article_id=self.object.pk, slug=self.slug)
        if self.object.published == Article.REMOVED:  # Block requests for REMOVED articles
            raise PermissionDenied()
        return super().render_to_response(context, **response_kwargs)


def patron_articles(request):
    data = {"title": "Early Article Access", "upcoming": Article.objects.upcoming(), "unpublished": Article.objects.unpublished()}
    data["wrong_password"] = True if request.POST.get("secret") and request.POST["secret"] not in [PASSWORD2DOLLARS, PASSWORD5DOLLARS] else False
    data["meta_context"] = {
        "description": [
            "name",
            "Take a look at these {} unpublished articles currently available to Worlds of ZZT patrons!".format(
                len(data["upcoming"]) + len(data["unpublished"])
            )
        ],
        "og:title": ["property", data["title"] + " - Museum of ZZT"],
        "og:image": ["property", "pages/early-access-preview.png"]
    }
    return render(request, "museum_site/patreon_articles.html", data)


def article_lock(request, article_id, slug=""):
    """ Page shown when a non-public article is attempted to be viewed """
    article = Article.objects.get(pk=article_id)

    if article.published == Article.PUBLISHED:  # Don't show a lock page for published articles
        return redirect(article.url())

    article.init_model_block_context("detailed", request=request)
    article.allow_comments = False
    data = {"title": "Restricted Article", "article": article, "cost": article.early_access_price, "release": article.publish_date}
    return render(request, "museum_site/article_lock.html", data)


def article_search(request):
    """ Returns page containing multiple filters to use when searching """
    form = Article_Search_Form(request.GET if request.GET else None)

    if request.session.get("DEBUG"):
        form.fields["sort"].choices += [
            ("-id", "!ID New"),
            ("id", "!ID Old"),
        ]

    data = {"title": "Article Search", "form": form}
    return render(request, "museum_site/generic-form-display.html", data)
