from django.views.generic import ListView
from museum_site.common import *
from museum_site.constants import NO_PAGINATION

class Directory_View(ListView):
    """ https://docs.djangoproject.com/en/3.2/ref/class-based-views/base/#django.views.generic.base.View.setup """
    template_name = "museum_site/generic-directory.html"
    model = None
    title = "Directory"
    paginate_by = 25
    context_object_name = "page"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.url_name = self.request.resolver_match.url_name

        # Get view format
        self.view = get_selected_view_format(
            self.request, self.model.supported_views
        )

        if self.model is not None:
            self.title = "{} Directory".format(self.model.model_name)

        # Get table header for list views
        if self.view == "list":
            self.paginate_by = 250  # Show more results on list pages
            if self.model is not None and self.view == "list":
                self.table_header = table_header(self.model.table_fields)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if hasattr(self, "table_header"):
            context["table_header"] = self.table_header
        context["title"] = self.title
        context["available_views"] = self.model.supported_views
        context["view"] = self.view
        context["sort_options"] = self.model.sort_options

        if self.paginate_by != NO_PAGINATION:
            context["page_number"] = context["page_obj"].number
            context["page_range"] = get_page_range(
                context["page_obj"].number,
                context["paginator"].num_pages
            )

        context["page"] = context["page_obj"]
        return context
