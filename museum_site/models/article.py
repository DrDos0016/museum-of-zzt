import os

from datetime import datetime

from django.db import models
from django.db.models import Q
from django.template import Template, Context
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from museum.settings import STATIC_URL
from museum_site.models.base import BaseModel
from museum_site.common import STATIC_PATH, epoch_to_unknown


class ArticleManager(models.Manager):
    def credited_authors(self):
        return self.exclude(Q(author="Unknown") | Q(author="N/A"))

    def in_early_access(self):
        return self.exclude(
            Q(published=Article.PUBLISHED) | Q(published=Article.REMOVED)
        ).order_by("publish_date", "id")

    def published(self):
        return self.filter(published=Article.PUBLISHED)

    def upcoming(self):
        return self.filter(published=Article.UPCOMING).order_by(
            "publish_date", "id"
        )

    def unpublished(self):
        return self.filter(published=Article.UNPUBLISHED).order_by(
            "publish_date", "id"
        )

    def removed(self):
        return self.filter(published=Article.REMOVED)

    def not_removed(self):
        return self.exclude(published=Article.REMOVED)

    def publication_packs(self):
        return self.filter(
            category="Publication Pack", published=Article.PUBLISHED
        ).order_by("-publish_date", "-id")

    def spotlight(self):
        return self.filter(
            published=Article.PUBLISHED, spotlight=True
        ).order_by("-publish_date", "id")

    def search(self, p):
        qs = self.exclude(published=Article.REMOVED)

        # Filter by series first as it excludes almost all articles
        if p.get("series") and p["series"] != "Any":
            qs = qs.filter(series=p["series"])

        if p.get("title"):
            qs = qs.filter(
                title__icontains=p["title"].strip()
            )
        if p.get("author"):
            qs = qs.filter(
                author__icontains=p["author"].strip()
            )
        if p.get("text"):
            qs = qs.filter(
                content__icontains=p["text"].strip()
            )
        if p.get("year"):
            if p["year"] == "Any":
                None
            elif p["year"] == "Unk":
                None
            else:
                year = p["year"].strip()
                qs = qs.filter(
                    publish_date__gte=year + "-01-01",
                    publish_date__lte=year + "-12-31",
                )

        if p.getlist("category"):
            qs = qs.filter(category__in=p.getlist("category"))

        # Get related files
        qs = qs.prefetch_related("file_set")

        return qs


class Article(BaseModel):
    """ Article object repesenting an article """
    model_name = "Article"
    table_fields = ["Title", "Author", "Date", "Category", "Description"]
    sort_options = [
        {"text": "Newest", "val": "-date"},
        {"text": "Oldest", "val": "date"},
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
        {"text": "Category", "val": "category"},
    ]

    SCHEMAS = (
        ("text", "Plaintext"),
        ("md", "Markdown"),  # TODO NOT WORKING 2022 (but also not used)
        ("html", "HTML"),
        ("django", "Django"),
        ("80col", "80 Column Text"),
    )

    REMOVED = 0
    PUBLISHED = 1
    UPCOMING = 2
    UNPUBLISHED = 3

    PUBLICATION_STATES = (
        (PUBLISHED, "Published"),
        (UPCOMING, "Upcoming"),
        (UNPUBLISHED, "Unpublished"),
        (REMOVED, "Removed"),
    )

    EARLY_ACCESS_PRICING = {
        UPCOMING: "$2.00 USD",
        UNPUBLISHED: "$5.00 USD",
    }

    objects = ArticleManager()

    # Fields
    title = models.CharField(
        help_text="Title of the the article.",
        max_length=100
    )
    author = models.CharField(
        help_text="Author(s) of the article. Slash separated.",
        max_length=50
    )
    category = models.CharField(
        help_text="Categorization of the article.",
        max_length=50
    )
    content = models.TextField(
        help_text="Body of the article.",
        default=""
    )
    css = models.TextField(
        help_text="Custom CSS. Must include <style></style> if set.",
        default="", blank=True
    )
    schema = models.CharField(
        help_text="Schema for the article. Used to determine parsing method.",
        max_length=6,
        choices=SCHEMAS,
        default="django"
    )
    publish_date = models.DateField(
        help_text="Date the article was made public on the Museum",
        default="1970-01-01"
    )
    published = models.IntegerField(
        help_text="Publication Status",
        default=UNPUBLISHED,
        choices=PUBLICATION_STATES
    )
    last_modified = models.DateTimeField(
        help_text="Date DB entry was last modified",
        auto_now=True,
    )
    last_revised = models.DateTimeField(
        help_text="Date article content was last revised",
        default=None, null=True, blank=True
    )
    revision_details = models.TextField(
        help_text="Reference for revisions made to the article",
        default="", blank=True
    )
    description = models.CharField(
        help_text="Blurb to summarize/pique interest in the article",
        max_length=250, default="", blank=True
    )
    allow_comments = models.BooleanField(
        help_text="Add a section for Disqus comments.",
        default=False
    )
    spotlight = models.BooleanField(
        help_text="Allow this article to be visible on the front page",
        default=True
    )
    static_directory = models.CharField(
        max_length=120,
        default="", blank=True,
        help_text=("Name of directory where static files for the article are "
                   "stored:<br>"
                   "/museum_site/static/articles/[year|unk]/[static_directory]")
    )
    secret = models.CharField(
        help_text=("Per-article key to allow non-patrons to read "
                   "unpublished articles"),
        max_length=12, default="", blank=True
    )

    # Associations
    series = models.ManyToManyField("Series", default=None, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        output = "[{}] {} by {}".format(self.id, self.title, self.author)
        return output

    def save(self, *args, **kwargs):
        # Update dates for series
        if self.id is not None:
            if self.series is not None:
                all_series = self.series.all()
                if all_series:
                    for s in all_series:
                        s.save()
        super(Article, self).save(*args, **kwargs)

    def url(self):
        output = "/article/{}/{}/".format(self.id, slugify(self.title))
        return output

    def preview_url(self):
        return os.path.join(STATIC_URL, self.path(), "preview.png")

    def path(self):
        year = self.publish_date.year
        if self.publish_date.year == 1970:
            year = "unk"

        return ("articles/{}/{}/".format(year, self.static_directory))

    def render(self):
        """ Render article content as a django template """
        context_data = {
            "TODO": "TODO", "CROP": "CROP",
            "path": self.path,
        }
        head = "{% load static %}\n{% load site_tags %}\n{% load zzt_tags %}"
        return Template(head + self.content).render(Context(context_data))

    @property
    def is_restricted(self):
        if self.published in [Article.UPCOMING, Article.UNPUBLISHED]:
            return True
        return False

    @property
    def published_string(self):
        """ Returns a human readable string for the article's publication
        state. """
        return Article.PUBLICATION_STATES[self.published - 1][1].lower()

    def series_links(self):
        """ Returns HTML links to related series """
        output = ""

        for s in self.series.all():
            output += '<a href="{}">{}</a>, '.format(s.url(), s.title)

        return output[:-2]

    def series_range(self):
        """ Returns a list of Articles with this article in the middle """
        output = []
        # TODO Better handling an article being in multiple series
        series = self.series.all().first()

        found_self = False
        remaining = 2
        for a in series.article_set.all().order_by("publish_date"):
            if remaining < 1:
                break
            if found_self:
                remaining -= 1

            output.append(a)

            if a.id == self.id:
                found_self = True

        return output[-5:]

    def get_series_links(self):
        output = []
        for s in self.series.only("id", "title"):
            output.append({"url": s.url, "text": s.title})
        return output

    def get_zfile_links(self):
        output = []
        for zf in self.file_set.all().order_by("sort_title"):
            output.append({"url": zf.url, "text": zf.title})
        return output

    @property
    def early_access_price(self):
        return self.EARLY_ACCESS_PRICING.get(self.published, "???")

    def initial_context(self, *args, **kwargs):
        context = super(Article, self).initial_context(*args, **kwargs)
        context["hash_id"] = "article-{}".format(self.pk)

        if hasattr(self, "extra_context"):
            context.update(self.extra_context)

            if self.extra_context.get("password_qs"):
                context["url"] = context["url"] + self.extra_context["password_qs"]

        return context

    def detailed_block_context(self, extras=None, *args, **kwargs):
        """ Return info to populate a detail block """
        context = self.initial_context(*args, **kwargs)
        context.update(
            title={"datum": "title", "value":self.title, "url":self.url()},
            columns=[],
        )

        if self.published == self.UPCOMING:
            context["title"]["roles"] = [
                "restricted", "article-upcoming"
            ]
        elif self.published == self.UNPUBLISHED:
            context["title"]["roles"] = [
                "restricted", "article-unpublished"
            ]

        context["columns"].append([
            {"datum": "text", "label": "Author", "value":self.author},
            {"datum": "text", "label": "Date", "value":epoch_to_unknown(self.publish_date)},
            {"datum": "text", "label": "Category", "value":self.category},
        ])

        if self.file_set.exists():
            context["columns"][0].append(
            {"datum": "multi-link", "label": "Associated Files", "values":self.get_zfile_links()}
        )

        context["columns"][0].append({"datum": "text", "label": "Description", "value":self.description})

        if self.series.count():
            context["columns"][0].append(
                {"datum": "multi-link", "label":"Series", "values":self.get_series_links()}
            )

        return context

    def list_block_context(self, extras=None, *args, **kwargs):
        context = self.initial_context(*args, **kwargs)
        context.update(
            pk=self.pk,
            model=self.model_name,
            hash_id="article-{}".format(self.pk),
            url=self.url,
            cells=[
                {"datum": "link", "url":self.url(), "value":self.title, "tag":"td"},
                {"datum": "text", "value": self.author, "tag":"td"},
                {"datum": "text", "value": epoch_to_unknown(self.publish_date), "tag":"td"},
                {"datum": "text", "value": self.category, "tag":"td"},
                {"datum": "text", "value": self.description, "tag":"td"},
            ],
        )

        if self.is_restricted:
            context["cells"][0]["roles"] = ["restricted"]

        return context

    def gallery_block_context(self, extras=None, *args, **kwargs):
        context = self.initial_context(*args, **kwargs)
        context.update(
            title={"datum": "title", "url":self.url(), "value":self.title},
            columns=[],
        )

        context["columns"].append([
            {"datum": "text", "value":self.author}
        ])


        if self.is_restricted:
            context["title"]["roles"] = ["restricted"]
        return context
