import math
import re

from django.views.generic.edit import FormView
from django.views.generic import ListView

from museum_site.constants import *
from museum_site.forms.review_forms import Review_Search_Form
from museum_site.generic_model_views import Model_Search_View, Model_List_View
from museum_site.models import *


class Reviewer_Directory_View(ListView):
    model = Review
    title = "Reviewer Directory"
    category = "Reviewer"
    template_name = "museum_site/generic-listing.html"
    url_name = "review_browse_author"
    query_string = ""

    def get_queryset(self):
        qs = Review.objects.reviewer_directory()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["url_name"] = self.url_name
        context["query_string"] = self.query_string
        context["items"] = []

        # Break the list of results into 4 columns
        db_author_list = sorted(self.object_list, key=lambda s: re.sub(r'(\W|_)', "é", s.lower()))

        for entry in db_author_list:
            item = {"name": entry, "letter": ""}
            if entry[0] in "1234567890":
                item["letter"] = "#"
            elif entry[0].upper() not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                item["letter"] = "*"
            else:
                item["letter"] = entry[0].upper()

            context["items"].append(item)

        context["split"] = math.ceil(len(context["items"]) / 4.0)
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

        if self.request.GET:
            context["search_type"] = "Advanced"
            context["query_edit_url_name"] = "review_search"
        return context




class Review_Search_View(Model_Search_View):
    form_class = Review_Search_Form
    model = Review
    model_list_view_class = Review_List_View
    template_name = "museum_site/generic-form-display.html"
    title = "Review Search"
