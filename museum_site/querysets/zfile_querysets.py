from random import randint, seed, shuffle

from django.db import models
from django.db.models import Q

from museum_site.querysets.base import Base_Queryset
from museum_site.core.detail_identifiers import *
from museum_site.core.zeta_identifiers import *

class ZFile_Queryset(Base_Queryset):
    def advanced_search(self, p):
        qs = self.all()

        # Filter by simple fields
        for f in ["title", "author", "filename", "company"]:
            if p.get(f):
                field = "{}__icontains".format(f)
                if f == "company": # TODO temporary hotfix
                    field = "ssv_company__icontains"
                value = p[f]
                qs = qs.filter(**{field: value})

        # Filter by genre
        if p.get("genre"):
            g = Genre.objects.filter(title=p["genre"]).first()
            if g:
                qs = qs.filter(genres=g)

        # Filter by language
        if p.get("lang"):
            if p["lang"] == "non-english":
                qs = qs.exclude(language="en")
            else:
                qs = qs.filter(language__icontains=p["lang"])

        # Filter by release year
        if p.get("year"):
            year = p["year"]
            if year.lower() == "unk":  # Unknown release year
                qs = qs.filter(release_date=None)
            else:  # Numeric years
                qs = qs.filter(release_date__gte="{}-01-01".format(year), release_date__lte="{}-12-31".format(year))

        # Filter by rating
        if p.get("min") and float(p["min"]) > 0:
            qs = qs.filter(rating__gte=float(p["min"]))
        if p.get("max") and float(p["max"]) < 5:
            qs = qs.filter(rating__lte=float(p["max"]))

        # Filter by playable/total board counts
        if p.get("board_min") and int(p["board_min"]) > 0:
            field = p.get("board_type", "total") + "_boards__gte"
            qs = qs.filter(**{field: int(p["board_min"])})
        if p.get("board_max") and int(p["board_max"]) <= 32767:
            field = p.get("board_type", "total") + "_boards__lte"
            qs = qs.filter(**{field: int(p["board_max"])})

        # Filter by items with/without reviews
        if p.get("reviews") == "yes":
            qs = qs.filter(review_count__gt=0)
        elif p.get("reviews") == "no":
            qs = qs.filter(review_count=0)

        # Filter by items with/without articles
        if p.get("articles") == "yes":
            qs = qs.filter(article_count__gt=0)
        elif p.get("articles") == "no":
            qs = qs.filter(article_count=0)

        if p.get("contents"):
            qs = qs.filter(content__title__icontains=p["contents"])

        # Filter by details
        if p.get("details"):
            qs = qs.filter(details__id__in=p.getlist("details"))

        qs = qs.distinct()
        return qs

    def basic_search(self, q, include_explicit=True):
        if include_explicit:
            return self.filter(
                Q(title__icontains=q) | Q(aliases__alias__icontains=q) | Q(author__icontains=q) | Q(filename__icontains=q) | Q(ssv_company__icontains=q)
            ).distinct()
        else:
            qs = self.filter(
                Q(title__icontains=q) | Q(aliases__alias__icontains=q) | Q(author__icontains=q) | Q(filename__icontains=q) | Q(ssv_company__icontains=q)
            ).filter(explicit=False).distinct()
            return qs

    def directory(self, category):
        if category == "company":
            return self.values("ssv_company").exclude(ssv_company=None).exclude(ssv_company="").distinct().order_by("ssv_company")
        elif category == "author":
            return self.values("author").distinct().order_by("author")

    def new_releases(self, spotlight_filter=False):
        """ Return zfiles without UPLOADED detail optionally spotlight-only ordered by newest release date """
        qs = self.exclude(details__id=DETAIL_UPLOADED)
        if spotlight_filter:
            qs = qs.spotlight()
        qs = qs.order_by("-release_date", "-id")
        return qs

    def new_finds(self, spotlight_filter=False):
        """ Return zfiles with NEW_FIND detail optionally spotlight-only ordered by newest publication date """
        qs = self.filter(details__id=DETAIL_NEW_FIND)
        if spotlight_filter:
            qs = qs.spotlight()
        qs = qs.order_by("-publish_date", "-id")
        return qs

    def published(self):
        """ Return zfiles lacking UPLOADED/LOST details """
        return self.exclude(details__id__in=[DETAIL_UPLOADED, DETAIL_LOST])

    def search(self, p):
        if p.get("q"):
            return self.basic_search(p["q"])
        else:
            qs = self.all()
        return qs

    def zeta_compatible(self):
        """ Return zfiles with supported Zeta details (ZZT/SZZT/UPLOADED/WEAVE) and excluded those with a RESTRICTED Zeta config """
        return self.filter(details__id__in=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED, DETAIL_WEAVE]).exclude(zeta_config__id=ZETA_RESTRICTED)

    def random_zfile(self, include_explicit=False, detail_filter=None):
        """ Returns a random zfile - Intended for API calls """
        # TODO: Return to this (note left 9/4/22)
        excluded_details = [DETAIL_REMOVED]
        qs = self.exclude(details__id__in=excluded_details)
        if not include_explicit:
            qs = qs.exclude(explicit=True)
        if detail_filter is not None:
            qs = qs.filter(details__id=detail_filter)

        zgame = qs.order_by("?").first()
        return zgame


    def random_zzt_world(self):
        """ Returns a random zfile with ZZT detail, excluding LOST/REMOVED/UPLOADED/CORRUPT details, and excluding EXPLICIT status """
        excluded_details = [DETAIL_LOST, DETAIL_REMOVED, DETAIL_UPLOADED, DETAIL_CORRUPT]
        max_pk = self.all().order_by("-id")
        if len(self.all()) == 0:
            return None
        max_pk = max_pk[0].id

        zgame = None
        while not zgame:
            pk = randint(1, max_pk)
            zgame = self.filter(pk=pk, details__id=DETAIL_ZZT).exclude(details__id__in=excluded_details).exclude(explicit=True)
            if zgame:
                return zgame.first()
        return zgame

    def roulette(self, rng_seed, limit):
        """ Returns a random sample of zfiles with ZZT/SZZT/WEAVE details, and excluding EXPLICIT status """
        details = [DETAIL_ZZT, DETAIL_SZZT, DETAIL_WEAVE]

        # Get all valid file IDs. Shuffle. Return in random order.
        ids = list(self.filter(details__id__in=details, explicit=False).values_list("id", flat=True))
        seed(rng_seed)
        shuffle(ids)
        return self.filter(id__in=ids[:limit]).order_by("?")

    def unpublished(self):
        """ Returns zfiles with UPLOADED detail. Used for cache calculation. Not actually used for Upload Queue page """
        return self.filter(details=DETAIL_UPLOADED)

    def wozzt(self):
        """ Returns zfiles with ZZT detail, lacking UPLOADED/GFX/LOST/CORRUPT details, and excluding EXPLICIT status """
        # Also excludes ry0. For reasons that become obvious when not excluded.
        excluded_details = [DETAIL_UPLOADED, DETAIL_GFX, DETAIL_LOST, DETAIL_CORRUPT]
        return self.filter(details__in=[DETAIL_ZZT]).exclude(
            Q(details__in=excluded_details) |
            Q(author__icontains="_ry0suke_") |
            Q(explicit=True)
        )

    def featured_worlds(self):
        """ Returns zfiles with FEATURED detail. """
        return self.filter(details=DETAIL_FEATURED)