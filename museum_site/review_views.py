from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic.edit import FormView
from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *
from museum_site.base_views import *
from museum_site.forms import Review_Search_Form

class Review_Directory_View(Directory_View):
    """ https://docs.djangoproject.com/en/3.2/ref/class-based-views/base/#django.views.generic.base.View.setup """
    model = Review
    title = "{} Directory".format(model.model_name)

    def get_queryset(self):
        author = self.kwargs.get("author")
        sort_by = self.request.GET.get("sort")

        if author is None:
            qs = Review.objects.filter(approved=True).select_related("zfile", "user")

            # Search filters
            if self.request.GET.get("title"):
                qs = qs.filter(title__icontains=self.request.GET["title"])
            if self.request.GET.get("author"):
                qs = qs.filter(author__icontains=self.request.GET["author"])
            if self.request.GET.get("review_date") and self.request.GET["review_date"] != "any":
                qs = qs.filter(date__year=self.request.GET["review_date"])

            if self.request.GET.get("ratingless"):
                if self.request.GET.get("min_rating"):
                    qs = qs.filter(Q(rating__gte=self.request.GET["min_rating"]) | Q(rating=-1))
                if self.request.GET.get("max_rating"):
                    qs = qs.filter(Q(rating__lte=self.request.GET["max_rating"]) | Q(rating=-1))
            else:
                if self.request.GET.get("min_rating"):
                    qs = qs.filter(rating__gte=self.request.GET["min_rating"])
                if self.request.GET.get("max_rating"):
                    qs = qs.filter(rating__lte=self.request.GET["max_rating"])

            if self.request.GET.get("text"):
                qs = qs.filter(content__itcointains=request.GET["text"])
            else:
                qs = qs.defer("content")
        else: # Reviews by author
            qs = Review.objects.filter(approved=True, author=author).select_related("zfile", "user").defer("content")

        qs = sort_qs(qs, sort_by, Review.sort_keys, "-date")
        return qs

class Review_Search_Form_View(FormView):
    model = Review
    form_class = Review_Search_Form
    template_name = "museum_site/review-search.html"
    title = "Review Search"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context

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
