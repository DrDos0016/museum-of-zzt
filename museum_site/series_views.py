from museum_site.generic_model_views import Model_List_View
from museum_site.models import Article, Series


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
        qs = self.head_object.article_set.accessible()
        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Series Overview - {}".format(self.head_object.title)
        context["prefix_text"] = "<h2>Articles in Series</h2>"
        return context
