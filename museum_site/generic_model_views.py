from time import time

from django.views.generic import ListView
from django.shortcuts import redirect

from museum_site.models import *
from museum_site.common import PAGE_SIZE, LIST_PAGE_SIZE, PAGE_LINKS_DISPLAYED, get_selected_view_format, get_sort_options, table_header, clean_params
from museum_site.constants import NO_PAGINATION


class Model_List_View(ListView):
    template_name = "museum_site/new-generic-directory.html"
    allow_pagination = True
    paginate_by = NO_PAGINATION

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.view = get_selected_view_format(self.request, self.model.supported_views)
        if self.allow_pagination:
            self.paginate_by = PAGE_SIZE if self.view != "list" else LIST_PAGE_SIZE
        self.sorted_by = request.GET.get("sort")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["available_views"] = self.model.supported_views
        context["view"] = self.view
        context["sort_options"] = get_sort_options(self.model.sort_options, debug=self.request.session.get("DEBUG"))
        context["sort"] = self.sorted_by
        context["model_name"] = self.model.model_name
        context["page_range"] = self.get_nearby_page_range(context["page_obj"].number, context["paginator"].num_pages)

        # Set block based on view
        context["block_template"] = "museum_site/blocks/new-generic-{}-block.html".format(context["view"])

        # Set title
        context["title"] = self.get_title()

        # Set head object if one is used
        context["head_object"] = self.head_object if hasattr(self, "head_object") else None

        # Initialize objects' local contexts
        for i in context["object_list"]:
            if self.view == "detailed":
                i.context = i.detailed_block_context()
            elif self.view == "list":
                i.context = i.list_block_context()
                context["table_header"] = table_header(self.model.table_fields)
            elif self.view == "gallery":
                i.context = i.gallery_block_context()

        return context

    def get_title(self):
        return "{} Directory".format(self.model.model_name)

    def sort_queryset(self, qs):
        fields = self.model.sort_keys.get(self.sorted_by)
        if fields is not None:
            qs = qs.order_by(fields)
        return qs

    def get_nearby_page_range(self, current_page, total_pages):
        # Determine lowest and highest visible page
        lower = max(1, current_page - (PAGE_LINKS_DISPLAYED // 2))
        upper = lower + PAGE_LINKS_DISPLAYED

        # Don't display too many pages
        if upper > total_pages + 1:
            upper = total_pages + 1

        page_range = range(lower, upper)
        return page_range


class ZFile_List_View(Model_List_View):
    model = File
    letter = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.letter = self.kwargs.get("letter")
        self.genre_slug = self.kwargs.get("genre_slug")
        self.detail_slug = self.kwargs.get("detail_slug")

        self.search_type = None
        self.detail = None
        self.genre = None

        if request.path == "/file/search/":
            self.search_type = "basic" if request.GET.get("q") else "advanced"

        # Default sort based on path
        if self.sorted_by is None:
            if request.path == "/file/browse/":
                self.sorted_by = "-publish_date"
            if request.path == "/detail/view/uploaded/":
                self.sorted_by = "uploaded"
            if request.path == "/file/roulette/":
                self.sorted_by = "random"

    def get_queryset(self):
        qs = File.objects.search(self.request.GET)

        if self.letter:
            qs = qs.filter(letter=self.letter)
        elif self.genre_slug:
            self.genre = Genre.objects.get(slug=self.genre_slug)
            qs = qs.filter(genres=self.genre)
        elif self.detail_slug:
            self.detail = Detail.objects.get(slug=self.detail_slug)
            qs = qs.filter(details=self.detail)
        elif self.request.path == "/file/browse/new-finds/":
            qs = File.objects.new_finds()
        elif self.request.path == "/file/browse/new-releases/":
            qs = File.objects.new_releases()
        elif self.request.path == "/file/roulette/":
            qs = File.objects.roulette(self.request.GET["seed"], PAGE_SIZE)  # Cap results for list view
        elif self.search_type == "advanced":
            cleaned_params = clean_params(self.request.GET.copy(), list_items=["details"])
            qs = File.objects.advanced_search(cleaned_params)

        # Pull in upload info
        qs = qs.prefetch_related("upload_set").distinct()

        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Modify sort options based on path
        if self.request.path == "/file/browse/":
            context["sort_options"] = [{"text": "Publish Date", "val": "-publish_date"}] + context["sort_options"]
        elif self.request.path == "/file/browse/new-finds/":
            context["sort_options"] = None
            context["sort"] = "-publish_date"
        elif self.request.path == "/file/browse/new-releases/":
            context["sort_options"] = None
            context["prefix_template"] = "museum_site/prefixes/new-releases.html"
        elif self.request.path == "/detail/view/uploaded/":
            context["sort_options"] = [{"text": "Upload Date", "val": "uploaded"}] + context["sort_options"]
        elif self.request.path == "/file/roulette/":
            context["sort_options"] = [{"text": "Random", "val": "random"}] + context["sort_options"]

        # Setup prefix text/template
        if self.detail:
            context["prefix_text"] = self.detail.description
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

        # Add advanced search modify button
        if self.search_type == "advanced":
            context["advanced_search"] = True

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
                return "Advanced Search Results"
            return title
        # Default
        return "Browse - All Files"


def prepare_roulette(request):
    """ Ensure a seed is provided to use for the roulette """
    if request.GET.get("seed"):
        return ZFile_List_View.as_view()(request)
    else:
        return redirect("/file/roulette/?seed={}".format(int(time())))


class Series_List_View(Model_List_View):
    model = Series
    queryset = Series.objects.directory()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = self.sort_queryset(qs)
        return qs


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
