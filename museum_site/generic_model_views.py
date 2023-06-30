from datetime import datetime, timezone, timedelta
from time import time

from django.db.models import Count
from django.shortcuts import redirect
from django.template.defaultfilters import slugify
from django.views.generic import DetailView, ListView

from museum_site.constants import PAGE_SIZE, LIST_PAGE_SIZE, NO_PAGINATION, PAGE_LINKS_DISPLAYED, MODEL_BLOCK_VERSION
from museum_site.core.detail_identifiers import DETAIL_UPLOADED, DETAIL_LOST
from museum_site.core.discord import discord_announce_review
from museum_site.core.form_utils import clean_params
from museum_site.core.misc import banned_ip
from museum_site.forms.review_forms import Review_Form
from museum_site.models import *
from museum_site.models import File as ZFile
from museum_site.settings import REMOTE_ADDR_HEADER
from museum_site.templatetags.site_tags import render_markdown
from museum_site.text import CATEGORY_DESCRIPTIONS


class Model_List_View(ListView):
    template_name = "museum_site/generic-directory-v{}.html".format(MODEL_BLOCK_VERSION)
    allow_pagination = True
    paginate_by = NO_PAGINATION
    has_local_context = True
    force_view = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.view = self.get_selected_view_format(self.request, self.model.supported_views)
        if self.force_view:
            self.view = self.force_view
        if self.allow_pagination:
            self.paginate_by = PAGE_SIZE if self.view != "list" else LIST_PAGE_SIZE
        self.sorted_by = request.GET.get("sort")

    def get_selected_view_format(self, request, available_views=["detailed", "list", "gallery"]):
        """ Determine which view should be used for model blocks. """
        # GET > Session > Default
        view = None
        if request.GET.get("view"):
            view = request.GET["view"]
        elif request.session.get("view"):
            view = request.session["view"]
        if view not in available_views:  # Default
            view = "detailed"
        request.session["view"] = view
        return view

    def get_sort_options(self, options, debug=False):
        output = options.copy()
        if debug:
            output += [{"text": "!ID New", "val": "-id"}, {"text": "!ID Old", "val": "id"}]
        return output

    def get_queryset(self):
        qs = super().get_queryset()
        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_views"] = self.model.supported_views
        context["view"] = self.view
        context["sort_options"] = self.get_sort_options(self.model.sort_options, debug=self.request.session.get("DEBUG"))
        context["sort"] = self.sorted_by
        context["model_name"] = self.model.model_name
        context["page_range"] = self.get_nearby_page_range(context["page_obj"].number, context["paginator"].num_pages)
        context["request"] = self.request
        context["debug"] = self.request.session.get("DEBUG")

        # Set title
        context["title"] = self.get_title()

        # Set head object if one is used
        context["head_object"] = self.head_object if hasattr(self, "head_object") else None

        return context

    def get_title(self):
        return "{} Directory".format(self.model.model_name)

    def sort_queryset(self, qs):
        fields = self.model.sort_keys.get(self.sorted_by)
        if fields is not None:
            qs = qs.order_by(*fields)
        return qs

    def get_nearby_page_range(self, current_page, total_pages):
        # Determine lowest and highest visible page
        lower = max(1, current_page - (PAGE_LINKS_DISPLAYED // 2))
        upper = lower + PAGE_LINKS_DISPLAYED
        upper = min(upper, total_pages + 1)
        page_range = range(lower, upper)
        return page_range


class ZFile_List_View(Model_List_View):
    model = ZFile
    letter = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.letter = self.kwargs.get("letter")
        self.search_type = None
        self.field = self.kwargs.get("field")
        self.value = self.kwargs.get("value")
        self.author = None
        self.company = None
        self.detail = None
        self.genre = None

        if request.path == "/file/search/":
            self.search_type = "basic" if request.GET.get("q") else "advanced"

        # Default sort based on path
        if self.sorted_by is None:
            if request.path == "/file/browse/":
                self.sorted_by = "-publish_date"
            if request.path == "/file/browse/detail/uploaded/":
                self.sorted_by = "uploaded"
            if request.path == "/file/roulette/":
                self.sorted_by = "random"

    def get_queryset(self):
        qs = ZFile.objects.search(self.request.GET)

        if self.letter:
            qs = qs.filter(letter=self.letter)
        elif self.request.path == "/file/browse/new-finds/":
            qs = ZFile.objects.new_finds()
        elif self.request.path == "/file/browse/new-releases/":
            qs = ZFile.objects.new_releases()
        elif self.request.path == "/file/roulette/":
            qs = ZFile.objects.roulette(self.request.GET["seed"], PAGE_SIZE)  # Cap results for list view
        elif self.search_type == "advanced":
            cleaned_params = clean_params(self.request.GET.copy(), list_items=["details"])
            qs = ZFile.objects.advanced_search(cleaned_params)
        elif self.value and self.field == "author":
            qs = qs.filter(authors__slug=self.value)
            self.author = Author.objects.reach(slug=self.value)
        elif self.value and self.field == "company":
            qs = qs.filter(companies__slug=self.value)
            self.company = Company.objects.reach(slug=self.value)
        elif self.value and self.field == "detail":
            qs = qs.filter(details__slug=self.value)
            self.detail = Detail.objects.reach(slug=self.value)
        elif self.value and self.field == "genre":
            qs = qs.filter(genres__slug=self.value)
            self.genre = Genre.objects.reach(slug=self.value)
        elif self.value and self.field == "year":
            if self.value == "unk":
                qs = qs.filter(release_date=None)
            else:
                qs = qs.filter(release_date__gte="{}-01-01".format(self.value), release_date__lte="{}-12-31".format(self.value))
        elif self.value and self.field == "language":
            qs = qs.filter(language__icontains=self.value)

        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_type"] = self.search_type

        # Modify sort options based on path
        if self.request.path == "/file/browse/":
            context["sort_options"] = [{"text": "Publish Date", "val": "-publish_date"}] + context["sort_options"]
        elif self.request.path == "/file/browse/new-finds/":
            context["sort_options"] = None
            context["sort"] = "-publish_date"
        elif self.request.path == "/file/browse/new-releases/":
            context["sort_options"] = None
            context["prefix_template"] = "museum_site/prefixes/new-releases.html"
        elif self.request.path == "/file/browse/detail/uploaded/":
            context["sort_options"] = [{"text": "Upload Date", "val": "uploaded"}] + context["sort_options"]
        elif self.request.path == "/file/roulette/":
            context["sort_options"] = [{"text": "Random", "val": "random"}] + context["sort_options"]

        # Setup prefix text/template
        if self.detail:
            context["prefix_text"] = self.detail.description
        if self.genre:
            context["prefix_text"] = self.genre.description
        if self.request.path == "/file/browse/new-finds/":
            context["prefix_template"] = "museum_site/prefixes/new-finds.html"
        if self.request.path == "/file/roulette/":
            context["prefix_template"] = "museum_site/prefixes/roulette.html"
        if self.request.GET.get("err") == "404":
            context["prefix_template"] = "museum_site/prefixes/file-404.html"

        # Debug cheat
        if self.request.GET.get("q") == "+DEBUG":
            self.request.session["DEBUG"] = 1
        elif self.request.GET.get("q") == "-DEBUG":
            del self.request.session["DEBUG"]

        # Add basic search filters
        if self.search_type == "basic":
            context["basic_search_fields"] = ["Title", "Author", "Company", "Genre", "Filename"]

        # Add search modify button
        context["query_edit_url_name"] = "advanced_search"

        # Remove view/sort widgets if no results were found
        if not context.get("object_list"):
            context["sort_options"] = None
            context["available_views"] = []

        return context

    def get_title(self):
        if self.letter:
            return "Browse - {}".format(self.letter.upper())
        elif self.genre:
            return "Browse Genre - {}".format(self.genre.title)
        elif self.detail:
            if self.detail.title == "Uploaded":
                return "Upload Queue"
            elif self.detail.title == "Featured World":
                return "Featured Worlds"
            return "Browse Detail - {}".format(self.detail.title)
        elif self.request.path == "/file/browse/new-finds/":
            return "New Finds"
        elif self.request.path == "/file/browse/new-releases/":
            return "New Releases"
        elif self.request.path == "/file/roulette/":
            return "Roulette"
        elif self.request.path == "/file/search/":
            title = 'Search Results - "{}"' .format(self.request.GET.get("q", ""))
            if self.request.GET.get("err") == "404":
                return "Automatic Search Results"
            elif self.search_type == "advanced":
                return "Search Results"
            return title
        elif self.request.path.startswith("/file/browse/author/") and self.author:
            return "Browse Author - {}".format(self.author.title)
        elif self.request.path.startswith("/file/browse/company/") and self.company:
            return "Browse Company - {}".format(self.company.title)
        elif self.request.path.startswith("/file/browse/genre/") and self.genre:
            return "Browse Genre - {}".format(self.genre.title)
        elif self.request.path.startswith("/file/browse/detail/") and self.detail:
            return "Browse Detail - {}".format(self.detail.title)
        elif self.request.path.startswith("/file/browse/year/"):
            return "Browse Year - {}".format(self.value)
        elif self.request.path.startswith("/file/browse/language/"):
            return "Browse Language - {}".format(self.value.upper())
        # Default
        return "Browse - All Files"


def prepare_roulette(request):
    """ Ensure a seed is provided to use for the roulette """
    if request.GET.get("seed"):
        return ZFile_List_View.as_view()(request)
    else:
        return redirect("/file/roulette/?seed={}".format(int(time())))


class ZFile_Article_List_View(Model_List_View):
    model = Article

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.sorted_by is None:
            self.sorted_by = "title"

    def get_queryset(self):
        key = self.kwargs.get("key")
        self.head_object = ZFile.objects.get(key=key)
        qs = Article.objects.accessible().filter(file=self.head_object)
        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["file"] = self.head_object
        context["head_object"] = None
        context["title"] = "{} - Articles".format(self.head_object.title)
        context["header_idx"] = 2
        return context


class ZFile_Review_List_View(Model_List_View):
    model = Review
    template_name = "museum_site/file-review.html"
    allow_pagination = False

    def get_queryset(self):
        key = self.kwargs.get("key")
        if key.lower().endswith(".zip"):
            key = key[:-4]
        self.head_object = ZFile.objects.get(key=key)
        qs = Review.objects.for_zfile_and_user(pk=self.head_object.pk, ip=self.request.META[REMOTE_ADDR_HEADER], user_id=self.request.user.id)
        self.qs = qs  # Needed to easily check for recent reviews later
        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["file"] = self.head_object
        context["title"] = "{} - Reviews".format(self.head_object.title)
        context["today"] = datetime.now(tz=timezone.utc)
        context["sort_options"] = [
            {"text": "Newest", "val": "-date"},
            {"text": "Oldest", "val": "date"},
            {"text": "Rating", "val": "rating"}
        ]

        # Check that the file supports reviews
        if not context["file"].can_review:
            context["cant_review_message"] = "This file is no longer accepting new reviews at this time."
            return context

        # Check for banned users
        if banned_ip(self.request.META[REMOTE_ADDR_HEADER]):
            context["cant_review_message"] = "<b>Banned account.</b>"
            return context

        # Prevent doubling up on reviews
        cutoff = context["today"] + timedelta(days=-1)
        recent = self.qs.filter(ip=self.request.META.get(REMOTE_ADDR_HEADER), date__gte=cutoff)
        if recent:
            context["cant_review_message"] = (
                "<i>You have <a href='#rev-{}'>recently reviewed</a> this file and cannot submit an additional review at this time.</i>".format(
                    recent.first().pk
                )
            )
            return context

        # Prevent unpublished/lost file reviews
        if context["file"].is_detail(DETAIL_UPLOADED):
            context["cant_review_message"] = "Unpublished files cannot be reviewed as their content may still be modified by the uploader."
            return context
        elif context["file"].is_detail(DETAIL_LOST):
            context["cant_review_message"] = "Lost files cannot be reviewed as they cannot be played!"
            return context

        # Initialize form
        review_form = Review_Form(self.request.POST) if self.request.POST else Review_Form()

        # Remove anonymous option for logged in users
        if self.request.user.is_authenticated:
            del review_form.fields["author"]

        # Post a review if one was submitted
        if self.request.POST and review_form.is_valid() and not recent:
            review = review_form.save(commit=False)
            if self.request.user.is_authenticated:
                review.author = self.request.user.username
                review.user_id = self.request.user.id
            review.ip = self.request.META.get(REMOTE_ADDR_HEADER)
            review.date = context["today"]
            review.zfile_id = self.head_object.id

            # Simple spam protection
            if self.head_object.can_review == File.REVIEW_APPROVAL or (review.content.find("href") != -1) or (review.content.find("[url=") != -1):
                review.approved = False
            if not self.request.user.is_authenticated and review.content.find("http") != -1:
                review_approved = False
            review.save()

            # Update file's review count/scores if the review is approved
            if self.head_object.can_review == ZFile.REVIEW_YES and review.approved:
                self.head_object.calculate_reviews()
                # Make Announcement
                discord_announce_review(review)
                self.head_object.save()

            # Re-get the queryset with the new review included and without including the form again
            context["object_list"] = self.get_queryset()
            context["recent"] = review.pk
            return context

        context["form"] = review_form
        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class Series_List_View(Model_List_View):
    model = Series
    queryset = Series.objects.directory()

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.sorted_by is None:
            self.sorted_by = "latest"


class Series_Contents_View(Model_List_View):
    model = Article
    allow_pagination = False

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.sorted_by is None:
            self.sorted_by = "-date"

    def get_queryset(self):
        pk = self.kwargs.get("series_id")
        self.head_object = Series.objects.get(pk=pk)
        qs = self.head_object.article_set.all()
        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Series Overview - {}".format(self.head_object.title)
        context["prefix_text"] = "<h2>Articles in Series</h2>"
        return context


class Review_List_View(Model_List_View):
    model = Review

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.sorted_by is None:
            self.sorted_by = "-date"
        self.author = self.kwargs.get("author")

    def get_queryset(self):
        if self.author:
            qs = Review.objects.search(p={"author": self.author})
        else:
            qs = Review.objects.search(self.request.GET)

        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.author:  # Don't allow sorting by reviewer when showing a single reviewer's reviews
            context["sort_options"].remove({"text": "Reviewer", "val": "reviewer"})

        # TODO: This properly adds the link, but the form isn't populated with the current search params
        # if self.request.GET:
        #    context["query_edit_url_name"] = "review_search"
        return context


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
        return context

    def get_title(self):
        if self.category:
            return "{} Directory".format(self.category)
        return super().get_title()


class Collection_List_View(Model_List_View):
    model = Collection

    def get_queryset(self):
        if self.request.path == "/collection/user/":
            qs = Collection.objects.collections_for_user(self.request.user.id)
        else:  # Default listing
            qs = Collection.objects.populated_public_collections()

        if self.sorted_by is None:
            self.sorted_by = "-modified"

        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prefix_template"] = "museum_site/prefixes/collection.html"
        return context

    def get_title(self):
        if self.request.path == "/collection/user/":
            return "My Collections"
        return super().get_title()


class Collection_Contents_View(Model_List_View):
    model = Collection_Entry

    def get_queryset(self):
        slug = self.kwargs.get("collection_slug")
        self.head_object = Collection.objects.get(slug=slug)
        qs = Collection_Entry.objects.get_items_in_collection(self.head_object.pk)

        if self.sorted_by is None:
            self.sorted_by = self.head_object.default_sort

        qs = self.sort_queryset(qs)
        # Remove duplicate entries -- TODO This seems quite janky
        if self.sorted_by in ["author", "company"]:
            pruned = []
            observed_ids = []
            for i in qs:
                if i.pk not in observed_ids:
                    observed_ids.append(i.pk)
                    pruned.append(i)
            return pruned

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.head_object.title
        context["prefix_text"] = "{}\n<h2>Collection Contents ({} file{})</h2>".format(
            render_markdown(self.head_object.description),
            self.head_object.item_count,
            ("" if self.head_object.item_count == 1 else "s")
        )

        # If there's no manual order available, don't show the option
        if context["head_object"].default_sort != "manual":
            context["sort_options"] = Collection_Entry.sort_options[1:]

        return context

    def render_to_response(self, context, **kwargs):
        # Prevent non-creators from viewing private collections
        if context["head_object"].visibility == Collection.PRIVATE:
            if self.request.user.id != context["head_object"].user_id:
                self.template_name = "museum_site/collection-invalid-permissions.html"
        return super().render_to_response(context, **kwargs)


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
                    "latest": {"url": cats[key].url(), "value": cats[key].title},
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


class Scroll_Detail_View(DetailView):
    model = Scroll
    template_name = "museum_site/scroll-detail.html"

    def get_queryset(self):
        qs = Scroll.objects.filter(identifier=self.kwargs["slug"], published=True)
        return qs

    def get_slug_field(self):
        return "identifier"
