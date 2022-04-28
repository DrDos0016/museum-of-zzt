from museum_site.models import *
from museum_site.base_views import *


class Series_Directory_View(Directory_View):
    model = Series
    title = "{} Directory".format(model.model_name)

    def get_queryset(self):
        sort_by = self.request.GET.get("sort")

        qs = self.model.objects.directory()

        if self.request.GET.get("sort") == "title":
            qs = qs.order_by("title")
        elif self.request.GET.get("sort") == "id":
            qs = qs.order_by("id")
        elif self.request.GET.get("sort") == "-id":
            qs = qs.order_by("-id")
        else:  # Default (Newest entry)
            qs = qs.order_by("-last_entry_date", "title")

        return qs


class Series_Overview_View(Directory_View):
    model = Series
    template_name = "museum_site/series-view.html"
    paginate_by = NO_PAGINATION

    def get_queryset(self):
        pk = self.kwargs.get("series_id")
        self.series = Series.objects.get(pk=pk)
        return self.series.article_set.all().order_by("publish_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Series Overview - {}".format(self.series.title)
        context["series"] = self.series
        return context
