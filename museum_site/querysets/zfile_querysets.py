from random import randint, seed, shuffle

from django.db.models import Q

from museum_site.core.detail_identifiers import *
from museum_site.core.zeta_identifiers import *
from museum_site.querysets.base import Base_Queryset


class ZFile_Queryset(Base_Queryset):
    def advanced_search(self, p):
        qs = self.all()

        # Filter by simple fields
        for f in ["title", "filename"]:
            if p.get(f):
                field = "{}__icontains".format(f)
                value = p[f]
                qs = qs.filter(**{field: value})

        # Filter by author
        if p.get("author"):
            qs = qs.filter(authors__title__icontains=p["author"])

        # Filter by company
        if p.get("company"):
            qs = qs.filter(companies__title__icontains=p["company"])

        # Filter by genre
        if p.get("genre"):
            qs = qs.filter(genres__title__icontains=p["genre"])

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
        if p.get("rating_min") and float(p["rating_min"]) > 0:
            qs = qs.filter(rating__gte=float(p["rating_min"]))
        if p.get("rating_max") and float(p["rating_max"]) < 5:
            qs = qs.filter(rating__lte=float(p["rating_max"]))

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
        qs = self.filter(
            Q(title__icontains=q) | Q(aliases__alias__icontains=q) | Q(authors__title__icontains=q) | Q(filename__icontains=q)
            | Q(companies__title__icontains=q) | Q(genres__title__icontains=q)
        )
        if not include_explicit:
            qs = qs.filter(explicit=False)
        return qs.distinct()

    def new_releases(self, spotlight_filter=False):
        """ Return zfiles without UPLOADED detail optionally spotlight-only ordered by newest release date """
        qs = self.exclude(details__id=DETAIL_UPLOADED)
        if spotlight_filter:
            qs = qs.spotlight()
        qs = qs.order_by("-release_date", "-id")
        return qs

    def new_releases_frontpage(self, spotlight_filter=False):
        qs = self.new_releases(spotlight_filter=spotlight_filter).exclude(details__id=DETAIL_NEW_FIND)
        qs = qs.order_by("-publish_date")
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

    def removed(self):
        return self.filter(details=DETAIL_REMOVED)

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
            Q(authors__title__icontains="_ry0suke_") |
            Q(explicit=True)
        )

    def featured_worlds(self):
        """ Returns zfiles with FEATURED detail. """
        return self.filter(details=DETAIL_FEATURED)

    def basic_search_suggestions(self, query="", match_anywhere=False):
        if not match_anywhere:
            query_filter = "title__istartswith"
        else:
            query_filter = "title__icontains"
        qs = self.filter(**{query_filter: query}).only("title").distinct().order_by("sort_title")
        return qs

    def zeta_config_audit(self):
        """ Return zfiles using special zeta configurations """
        return self.exclude(
            Q(zeta_config_id=None) |
            Q(zeta_config_id=ZETA_ZZT32R) |
            Q(zeta_config_id=ZETA_SZZT20)
        ).order_by("zeta_config")

    def unpublished_user_uploads(self, user_id):
        """ Returns zfiles uploaded by user_id that have remain unpublished """
        return self.filter(upload__user_id=user_id, details=DETAIL_UPLOADED).order_by("-id")
