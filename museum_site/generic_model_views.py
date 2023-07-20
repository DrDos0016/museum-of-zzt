from datetime import datetime, timezone, timedelta

from django.shortcuts import redirect
from django.template.defaultfilters import slugify
from django.views.generic import DetailView, FormView, ListView, TemplateView

from museum_site.constants import PAGE_SIZE, LIST_PAGE_SIZE, NO_PAGINATION, PAGE_LINKS_DISPLAYED, MODEL_BLOCK_VERSION
from museum_site.core.detail_identifiers import DETAIL_UPLOADED, DETAIL_LOST
from museum_site.core.discord import discord_announce_review
from museum_site.core.form_utils import clean_params
from museum_site.core.misc import banned_ip
from museum_site.models import *
from museum_site.models import File as ZFile
from museum_site.templatetags.site_tags import render_markdown


class Model_List_View(ListView):
    template_name = "museum_site/generic-directory-v{}.html".format(MODEL_BLOCK_VERSION)
    allow_pagination = True
    paginate_by = NO_PAGINATION
    has_local_context = True
    force_view = None
    non_search_params = {"sort", "view", "page"}  # Set of GET params that do not indicate a search is being performed

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.view = self.get_selected_view_format(self.request, self.model.supported_views)
        if self.force_view:
            self.view = self.force_view
        if self.allow_pagination:
            self.paginate_by = PAGE_SIZE if self.view != "list" else LIST_PAGE_SIZE
        self.sorted_by = request.GET.get("sort")
        self.searching = self.is_searching(self.request)

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
        context["searching"] = self.searching

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
        if request.GET and request.GET.get("action") != "edit":  # Show search results
            return self.model_list_view_class.as_view()(request, *args, **kwargs)
        else:  # Show search form
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        if self.request.GET:
            form_kwargs["data"] = self.request.GET
        return form_kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context

class Generic_Error_View(TemplateView):
    template_name = "museum_site/error.html"
