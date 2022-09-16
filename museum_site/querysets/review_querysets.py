from django.db import models
from django.db.models import Avg, Q

from museum_site.querysets.base import Base_Queryset
from museum_site.models import *

class Review_Queryset(Base_Queryset):
    def average_rating_for_zfile(self, zfile_id):
        return self.filter(zfile_id=zfile_id, rating__gte=0).aggregate(Avg("rating"))

    def latest_approved_reviews(self):
        return self.filter(approved=True).order_by("-date", "-id")

    def pending_approval(self):
        return self.filter(approved=False).order_by("-date", "-id")

    def reviewer_directory(self):
        return self.filter(approved=True).values_list("author", flat=True).distinct().order_by("author")

    def search(self, p):
        qs = self.filter(approved=True)

        # Filter by simple fields
        for f in ["title", "author", "content"]:
            if p.get(f):
                field = "{}__icontains".format(f)
                value = p[f]
                qs = qs.filter(**{field: value})

        if p.get("review_date") and p["review_date"] != "any":
            qs = qs.filter(date__year=p["review_date"])

        if p.get("ratingless"):
            if p.get("min_rating"):
                qs = qs.filter(Q(rating__gte=p["min_rating"]) | Q(rating=-1))
            if p.get("max_rating"):
                qs = qs.filter(Q(rating__lte=p["max_rating"]) | Q(rating=-1))
        else:
            if p.get("min_rating"):
                qs = qs.filter(rating__gte=p["min_rating"])
            if p.get("max_rating"):
                qs = qs.filter(rating__lte=p["max_rating"])

        # Include zfile and user information
        qs = qs.select_related("zfile", "user")
        # Don't pull review text unless searching by it
        if not p.get("content"):
            qs = qs.defer("content")
        return qs
