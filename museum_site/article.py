import os

from datetime import datetime

from django.db import models
from django.db.models import Q
from django.template import Template, Context
from django.template.defaultfilters import slugify

from museum.settings import STATIC_URL

from .constants import (
    PUBLISHED_ARTICLE, UPCOMING_ARTICLE, UNPUBLISHED_ARTICLE, REMOVED_ARTICLE,
)


ARTICLE_FORMATS = (
    ("text", "Plaintext"),
    ("md", "Markdown"),
    ("html", "HTML"),
    ("django", "Django"),
    ("80col", "80 Column Text"),
)

ARTICLE_PUBLISH = (
    (PUBLISHED_ARTICLE, "Published"),
    (UPCOMING_ARTICLE, "Upcoming"),
    (UNPUBLISHED_ARTICLE, "Unpublished"),
    (REMOVED_ARTICLE, "Removed"),
)


class ArticleManager(models.Manager):
    def credited_authors(self):
        return self.exclude(Q(author="Unknown") | Q(author="N/A"))

    def published(self):
        return self.filter(published=PUBLISHED_ARTICLE)

    def upcoming(self):
        return self.filter(published=UPCOMING_ARTICLE)

    def unpublished(self):
        return self.filter(published=UNPUBLISHED_ARTICLE)

    def removed(self):
        return self.filter(published=REMOVED_ARTICLE)

    def not_removed(self):
        return self.exclude(published=REMOVED_ARTICLE)

    def publication_packs(self):
        return self.filter(
            category="Publication Pack", published=PUBLISHED_ARTICLE
        ).order_by("-publish_date", "-id")

    def spotlight(self):
        return self.filter(
            published=PUBLISHED_ARTICLE, spotlight=True
        ).order_by("-publish_date", "id")

    def search(self, p):
        qs = self.exclude(published=REMOVED_ARTICLE)

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

        return qs


class Article(models.Model):
    """ Article object repesenting a page from an article"""

    objects = ArticleManager()

    """
    Fields:
    title           -- Title of the article
    author          -- Author of the article
    category        -- Categorization of the article for the directory
    content         -- Body of the article
    css             -- Custom CSS for the article
    schema          -- Whether the article is in text/md/html/django form
    publish_date    -- Date the article was written
    published       -- If the article is available to the public
    last_modified   -- Last time file was modified
    summary         -- Summary for Opengraph
    preview         -- Path to preview image
    allow_comments  -- Allow user comments on the article
    spotlight       -- Allow appearance on front page
    static_directory-- Directory for static files used in the article
    series          -- Series the article is a part of
    secret          -- Key to read this article early without being a patron
    """
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    content = models.TextField(default="")
    css = models.TextField(default="", blank=True)
    schema = models.CharField(
        max_length=6,
        choices=ARTICLE_FORMATS,
        default="django"
    )
    publish_date = models.DateField(default="1970-01-01")
    published = models.IntegerField(
        default=UNPUBLISHED_ARTICLE,
        choices=ARTICLE_PUBLISH
    )
    last_modified = models.DateTimeField(
        auto_now=True,
        help_text="Date DB entry was last modified"
    )
    last_revised = models.DateTimeField(
        help_text="Date article content was last revised",
        default=None, null=True, blank=True
    )
    revision_details = models.TextField(default="", blank=True)
    summary = models.CharField(max_length=150, default="", blank=True)
    allow_comments = models.BooleanField(default=False)
    spotlight = models.BooleanField(default=True)
    static_directory = models.CharField(
        max_length=120,
        default="", blank=True,
        help_text=("Name of directory where static files for the article are"
                   "stored.")
    )
    secret = models.CharField(max_length=12, default="", blank=True)

    # Associations
    series = models.ManyToManyField("Series", default=None, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        output = "[" + str(self.id) + "] " + self.title + " by " + self.author
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
        return "/article/" + str(self.id) + "/" + slugify(self.title)

    @property
    def preview(self):
        return os.path.join(STATIC_URL, self.path(), "preview.png")

    def path(self):
        if self.publish_date.year == 1970:
            year = "unk"
        else:
            year = self.publish_date.year
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
        if self.published in [UPCOMING_ARTICLE, UNPUBLISHED_ARTICLE]:
            return True
        return False

    @property
    def published_string(self):
        """ Returns a human readable string for the article's publication
        state. """
        return ARTICLE_PUBLISH[self.published - 1][1].lower()


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
