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
