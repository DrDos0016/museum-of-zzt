from django.db import models
from django.db.models import Q


class Article_Queryset(models.QuerySet):
    def credited_authors(self):
        """ Return qs of all named authors associated with at least one article """
        return self.exclude(Q(author="Unknown") | Q(author="N/A")).only("author")

    def in_early_access(self):
        """ Return qs of all articles that are currently paywalled """
        return self.exclude(
            Q(published=self.model.PUBLISHED) | Q(published=self.model.REMOVED)
        ).defer("content").order_by("publish_date", "id")

    def published(self):
        """ Return qs of all articles that are PUBLISHED """
        return self.filter(published=self.model.PUBLISHED)

    def upcoming(self):
        """ Return qs of all articles that are UPCOMING """
        return self.filter(published=self.model.UPCOMING).order_by("publish_date", "id")

    def unpublished(self):
        """ Return qs of all articles that are UNPUBLISHED """
        return self.filter(published=self.model.UNPUBLISHED).order_by("publish_date", "id")

    def removed(self):
        """ Return qs of all articles that are REMOVED """
        return self.filter(published=self.model.REMOVED)

    def not_removed(self):
        """ Return qs of all articles that are -NOT- REMOVED """
        return self.exclude(published=self.model.REMOVED)

    def publication_packs(self):
        """ Return qs of all articles that are PUBLISHED and categorized as Publication Packs """
        return self.filter(category="Publication Pack").published().defer("content").order_by("-publish_date", "-id")

    def spotlight(self):
        """ Return qs of all articles that are PUBLISHED and marked as being spotlight permitted """
        return self.filter(published=self.model.PUBLISHED, spotlight=True).defer("content").order_by("-publish_date", "-id")

    def search(self, p):
        qs = self.exclude(published=self.model.REMOVED)

        # Filter by series first as it excludes almost all articles
        if p.get("series") and p["series"] != "Any":
            qs = qs.filter(series=p["series"])

        if p.get("title"):
            qs = qs.filter(title__icontains=p["title"].strip())
        if p.get("author"):
            qs = qs.filter(author__icontains=p["author"].strip())
        if p.get("text"):
            qs = qs.filter(content__icontains=p["text"].strip())
        if p.get("year"):
            if p["year"] == "Any":
                None
            elif p["year"] == "Unk":
                None
            else:
                year = p["year"].strip()
                qs = qs.filter(publish_date__gte=year + "-01-01", publish_date__lte=year + "-12-31",)

        if p.getlist("category"):
            qs = qs.filter(category__in=p.getlist("category"))

        # Get related files
        qs = qs.prefetch_related("file_set")

        if not p.get("text"):
            qs = qs.defer("content")

        return qs
