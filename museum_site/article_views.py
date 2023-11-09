from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import slugify
from django.views.generic import DetailView, FormView

from museum_site.core.redirects import redirect_with_querystring
from museum_site.forms.article_forms import Article_Search_Form
from museum_site.models import Article, Article_Category_Block
from museum_site.generic_model_views import Model_List_View, Model_Search_View
from museum_site.text import CATEGORY_DESCRIPTIONS


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
        if self.object.published in [Article.IN_PROGRESS, Article.REMOVED]:  # Block requests for IN_PROGRESS/REMOVED articles
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
        return redirect(article.get_absolute_url())

    article.init_model_block_context("detailed", request=request)
    article.allow_comments = False
    data = {"title": "Restricted Article", "article": article, "cost": article.early_access_price, "release": article.publish_date}
    return render(request, "museum_site/article-lock.html", data)


def article_search(request):
    """ Returns page containing multiple filters to use when searching """
    if request.GET:
        return Article_Search_View.as_view()
    form = Article_Search_Form(request.GET if request.GET else None)

    if request.session.get("DEBUG"):
        form.fields["sort"].choices += [
            ("-id", "!ID New"),
            ("id", "!ID Old"),
        ]

    data = {"title": "Article Search", "form": form}
    return render(request, "museum_site/generic-form-display.html", data)


class Article_List_View(Model_List_View):
    model = Article

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.category_slug = kwargs.get("category_slug")
        self.category = None

        # Convert category slug to article.category string
        if self.category_slug:
            if self.category_slug == "lets-play":  # Special case for apostrophe
                self.category = "Let's Play"
            else:
                self.category = self.category_slug.replace("-", " ")
                self.category = self.category.title()

    def get_queryset(self):
        qs = Article.objects.search(self.request.GET)

        if self.category:
            qs = qs.filter(category=self.category)
        if self.sorted_by is None:
            self.sorted_by = "-date"

        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prefix_templates = {
            "closer-look": "museum_site/prefixes/closer-look.html",
            "livestream": "museum_site/prefixes/livestream.html",
            "publication-pack": "museum_site/prefixes/publication-pack.html",
        }

        if prefix_templates.get(self.category_slug):
            context["prefix_template"] = prefix_templates[self.category_slug]

        if self.request.GET:
            context["search_type"] = "Advanced"
            context["query_edit_url_name"] = "article_search"
        return context

    def get_title(self):
        if self.category:
            return "{} Directory".format(self.category)
        return super().get_title()



class Article_Categories_List_View(Model_List_View):
    model = Article
    allow_pagination = False
    has_local_context = False
    force_view = "detailed"

    def get_queryset(self):
        # Find the counts of each category
        counts = {}
        count_qs = Article.objects.accessible().values("category").annotate(total=Count("category")).order_by("category")
        for c in count_qs:
            counts[slugify(c["category"])] = c["total"]

        # Find the latest article of each category
        seen_categories = []
        cats = {}
        cats_qs = Article.objects.published().defer("content").order_by("-id")
        for a in cats_qs:
            if a.category not in seen_categories:
                seen_categories.append(a.category)
                cats[a.category_slug().lower()] = a
            if len(seen_categories) == len(Article.CATEGORY_CHOICES):
                break

        qs = []
        for key in CATEGORY_DESCRIPTIONS:
            if not cats.get(key):
                continue

            i = Article_Category_Block()
            i.set_initial_attributes(
                {
                    "title": cats[key].category,
                    "preview": {"url": "/pages/article-categories/{}.png".format(key), "alt": cats[key].title},
                    "article_count": counts[key],
                    "latest": {"url": cats[key].get_absolute_url(), "value": cats[key].title},
                    "description": CATEGORY_DESCRIPTIONS.get(key, "<i>No description available</i>")
                }
            )

            qs.append(i)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Article Categories"
        context["available_views"] = ["detailed"]
        context["sort_options"] = None
        context["disable_guide_words"] = True
        return context


class Article_Search_View(Model_Search_View):
    form_class = Article_Search_Form
    model = Article
    model_list_view_class = Article_List_View
    template_name = "museum_site/generic-form-display.html"
    title = "Article Search"
