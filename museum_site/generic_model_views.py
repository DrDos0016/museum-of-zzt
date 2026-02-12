from datetime import datetime, timezone, timedelta

from django.shortcuts import redirect
from django.template.defaultfilters import slugify
from django.urls import resolve
from django.views.generic import DetailView, FormView, ListView, TemplateView

from museum_site.constants import PAGE_SIZE, LIST_PAGE_SIZE, NO_PAGINATION, PAGE_LINKS_DISPLAYED, MODEL_BLOCK_VERSION
from museum_site.core.detail_identifiers import DETAIL_UPLOADED, DETAIL_LOST
from museum_site.core.discord import discord_announce_review
from museum_site.core.form_utils import clean_params
from museum_site.core.misc import Meta_Tag_Block
from museum_site.models import Article, File as ZFile
from museum_site.templatetags.site_tags import render_markdown


class Model_List_View(ListView):
    template_name = "museum_site/generic-directory-v{}.html".format(MODEL_BLOCK_VERSION)
    allow_pagination = True
    paginate_by = NO_PAGINATION
    has_local_context = True
    force_view = None
    non_search_params = {"sort", "view", "page"}  # Set of GET params that do not indicate a search is being performed
    head_object = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        default_sort = None
        if kwargs.get("field") == "year":  # Sort by date by default when browsing by year
            default_sort = "release"
        if kwargs.get("value") == "featured-world":
            default_sort = "recent"
        self.view = self.get_selected_view_format(self.request, self.model.supported_views)
        if self.force_view:
            self.view = self.force_view
        if self.allow_pagination:
            self.paginate_by = PAGE_SIZE if self.view != "list" else LIST_PAGE_SIZE
        self.sorted_by = request.GET.get("sort", default_sort)
        self.searching = self.is_searching(self.request)

    def get_selected_view_format(self, request, available_views=["detailed", "list", "gallery"]):
        """ Determine which view should be used for model blocks. """
        # GET > Session > Default
        view = None
        if request.GET.get("view"):
            view = request.GET["view"]
            request.session["view"] = view
        elif request.session.get("view"):
            view = request.session["view"]
        if view not in available_views:  # Default
            view = "detailed"
        return view

    def get_sort_options(self, options, debug=False):
        ## TODO: IS THIS USED
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
        context["sort_options"] = self.model.sorter().get_sort_options(include_tags=["basic", "debug" if self.request.session.get("DEBUG") else None, "featured" if self.kwargs.get("value") == "featured-world" else None])
        context["sort"] = self.sorted_by
        context["model_name"] = self.model.model_name
        context["page_range"] = self.get_nearby_page_range(context["page_obj"].number, context["paginator"].num_pages)
        context["request"] = self.request
        context["debug"] = self.request.session.get("DEBUG")
        context["searching"] = self.searching
        context["field"] = self.kwargs.get("field")
        context["field_value"] = self.kwargs.get("value")
        if self.kwargs.get("field") == "year":
            if self.kwargs["value"] == "unk":
                context["next_year"] = 1991
                context["prev_year"] = "unk"
                context["prev_year_text"] = "Unknown"
            else:
                context["next_year"] = int(self.kwargs["value"]) + 1
                context["prev_year"] = int(self.kwargs["value"]) - 1
                if context["prev_year"] < 1991:
                    context["prev_year"] = "unk"
                    context["prev_year_text"] = "Unknown"

        # Set title
        context["title"] = self.get_title()

        # Set head object if one is used
        context["head_object"] = self.head_object if hasattr(self, "head_object") else None

        context["meta_tags"] = self.get_meta_tags()
        return context

    def get_meta_tags(self):
        url = self.request.get_full_path()
        title = self.get_title()
        author = "Dr. Dos"  # Default

        key = resolve(self.request.path) if self.request.resolver_match else None
        path_specific_meta_tags = {
            "zfile_browse_letter": {"title": title},
            "zfile_browse": {"title": title},
            "collection_browse": {"title": title},
            "zfile_browse_field": {"title": title}, # This hits a lot of things
            "zfile_browse_new_finds": {"title": title},
            "zfile_browse_new_releases": {"title": title},
            "zfile_roulette": {"title": title},
            "series_view": {"title": title},
        }
        kwargs = path_specific_meta_tags.get(key.url_name, {"title":"PLACEHOLDER TITLE", "author":"PLACEHOLDER AUTHOR"})
        meta_tags = Meta_Tag_Block(url=url, **kwargs)
        return meta_tags

    def get_title(self):
        return "{} Directory".format(self.model.model_name)

    def sort_queryset(self, qs):
        if self.sorted_by == "recent":  # Recently Featured Worlds. Weird spot for this but welp
            return get_recently_featured_zfiles()
        db_ordering = self.model.sorter().get_db_ordering_for_value(self.sorted_by)
        if db_ordering is not None:
            qs = qs.order_by(*db_ordering)
        return qs

    def get_nearby_page_range(self, current_page, total_pages):
        # Determine lowest and highest visible page
        lower = max(1, current_page - (PAGE_LINKS_DISPLAYED // 2))
        upper = lower + PAGE_LINKS_DISPLAYED
        upper = min(upper, total_pages + 1)
        page_range = range(lower, upper)
        return page_range

    def is_searching(self, request):
        # Determine if this request is browsing or searching
        if request.GET:
            key_set = set(list(request.GET.keys()))
            diff = key_set - self.non_search_params
            if diff:
                return True
        return False


class Model_Search_View(FormView):
    def get(self, request, *args, **kwargs):
        destination = "form"
        if request.GET and request.GET.get("action") != "edit":  # Show search results if valid
            if request.GET.get("q"):  # Basic search
                destination = "results"
            else:
                form = self.form_class(request.GET)
                if form.is_valid():
                    destination = "results"

        if destination == "form":
            return super().get(request, *args, **kwargs)
        else:  # Results
            return self.model_list_view_class.as_view()(request, *args, **kwargs)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        if self.request.GET:
            form_kwargs["data"] = self.request.GET
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["meta_tags"] = Meta_Tag_Block(url=self.request.get_full_path(), title=self.title, description=self.description)
        return context


class Generic_Error_View(TemplateView):
    template_name = "museum_site/error.html"


# TODO should this live elsewhere probably
def get_recently_featured_zfiles():
    # Used for sorting by recently featured worlds when browsing featured worlds

    article_pks = list(Article.objects.filter(category="Featured World").order_by("-publish_date").values_list("pk", flat=True))
    temp_dict = {}
    for article_pk in article_pks:
        if article_pk in [44, 262, 134]: # MRWAIF Featued Game/MTP, Fool's Quest CGotM
            continue
        temp_dict[article_pk] = None

    unordered_zfiles = ZFile.objects.filter(articles__in=article_pks)

    for zfile in unordered_zfiles:
        if zfile.pk == 1852 or zfile.pk == 1334:  # MRWAIF / Warlord's Temple Beta
            continue
        zfile_article_pks = zfile.articles.filter(pk__in=article_pks).values_list("pk", flat=True)
        for article_pk in zfile_article_pks:
            temp_dict[article_pk] = zfile

    queryset = []
    seen = []
    for (k, v) in temp_dict.items():
        if v.pk not in seen:
            queryset.append(v)
            seen.append(v.pk)
    return queryset
