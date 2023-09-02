from django.shortcuts import redirect
from django.template.defaultfilters import slugify
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Scroll #{}".format(context["scroll"].pk)
        return context


def scroll_navigation(request, navigation="random"):
    VALID_NAVIGATIONS = ["next", "prev", "first", "latest", "random"]
    navigation = navigation if navigation in VALID_NAVIGATIONS else "random"
    scroll = None

    if request.GET.get("id"):
        ref = int(request.GET["id"])
        if navigation == "next":
            scroll = Scroll.objects.filter(published=True, pk__gt=ref).order_by("id").first()
        elif navigation == "prev":
            scroll = Scroll.objects.filter(published=True, pk__lt=ref).order_by("-id").first()
    else:
        if navigation == "first":
            scroll = Scroll.objects.filter(published=True).order_by("id").first()
        elif navigation == "latest":
            scroll = Scroll.objects.filter(published=True).order_by("-id").first()

    if not scroll:
        if navigation == "next":
            scroll = Scroll.objects.filter(published=True).order_by("-id").first()
        elif navigation == "prev":
            scroll = Scroll.objects.filter(published=True).order_by("id").first()
        else: # Random
            scroll = Scroll.objects.filter(published=True).order_by("?").first()

    slug = slugify(scroll.title) if scroll else "unlabeled-scroll"
    return redirect(scroll.get_absolute_url())
