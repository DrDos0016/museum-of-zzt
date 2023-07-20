from django.views.generic import DetailView

from museum_site.generic_model_views import Model_List_View
from museum_site.models import Scroll

class Scroll_List_View(Model_List_View):
    model = Scroll
    allow_pagination = True
    has_local_context = False
    force_view = "list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prefix_template"] = "museum_site/prefixes/scrolls-of-zzt.html"
        return context


class Scroll_Detail_View(DetailView):
    model = Scroll
    template_name = "museum_site/scroll-detail.html"

    def get_queryset(self):
        qs = Scroll.objects.filter(pk=self.kwargs["pk"], published=True)
        return qs

    def get_slug_field(self):
        return "identifier"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Scroll #{}".format(context["scroll"].pk)
        return context
