from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *
from museum_site.base_views import *

class Review_Directory_View(Directory_View):
    """ https://docs.djangoproject.com/en/3.2/ref/class-based-views/base/#django.views.generic.base.View.setup """
    model = Review
    title = "{} Directory".format(model.model_name)

    def get_queryset(self):
        author = self.kwargs.get("author")
        sort_by = self.request.GET.get("sort")

        if author is None:
            qs = Review.objects.filter(approved=True).select_related("zfile", "user").defer("content")
        else:
            qs = Review.objects.filter(approved=True, author=author).select_related("zfile", "user").defer("content")

        if sort_by == "date":
            qs = qs.order_by("date")
        elif sort_by == "file":
            qs = qs.order_by("zfile__sort_title")
        elif sort_by == "reviewer":
            qs = qs.order_by("author")
        elif sort_by == "rating":
            qs = qs.order_by("-rating")
        elif sort_by == "id":
            qs = qs.order_by("id")
        elif sort_by == "-id":
            qs = qs.order_by("-id")
        else:  # Default (newest)
            qs = qs.order_by("-date")

        return qs

class Reviewer_Directory_View(Directory_View):
    model = Review
    title = "Reviewer Directory"
    category = "Reviewer"
    template_name = "museum_site/generic-listing.html"
    url_name = "reviews_by_author"
    query_string = ""

    def get_queryset(self):
        qs = Review.objects.filter(approved=True).values_list("author", flat=True).distinct().order_by("author")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["url_name"] = self.url_name
        context["query_string"] = self.query_string
        context["items"] = []


        # Break the list of results into 4 columns
        db_author_list = sorted(
            self.object_list, key=lambda s: re.sub(r'(\W|_)', "é", s.lower())
        )

        for entry in db_author_list:
            item = {
                "name": entry,
                "letter": "",
            }
            if entry[0] in "1234567890":
                item["letter"] = "#"
            elif entry[0].upper() not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                item["letter"] = "*"
            else:
                item["letter"] = entry[0].upper()

            context["items"].append(item)

        context["split"] = math.ceil(len(context["items"]) / 4.0)
        return context
