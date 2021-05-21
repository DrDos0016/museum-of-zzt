import os

from datetime import datetime

from django.db import models
from django.template import Template, Context
from django.template.defaultfilters import slugify

from museum.settings import STATIC_URL

from .constants import (
    PUBLISHED_ARTICLE, UPCOMING_ARTICLE, UNPUBLISHED_ARTICLE, REMOVED_ARTICLE
)


ARTICLE_FORMATS = (
    ("text", "Plaintext"),
    ("md", "Markdown"),
    ("html", "HTML"),
    ("django", "Django"),
)

ARTICLE_PUBLISH = (
    (PUBLISHED_ARTICLE, "Published"),
    (UPCOMING_ARTICLE, "Upcoming"),
    (UNPUBLISHED_ARTICLE, "Unpublished"),
    (REMOVED_ARTICLE, "Removed"),
)


class Article(models.Model):
    """ Article object repesenting a page from an article

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
    summary = models.CharField(max_length=150, default="", blank=True)
    allow_comments = models.BooleanField(default=False)
    spotlight = models.BooleanField(default=True)
    static_directory = models.CharField(
        max_length=120,
        default="", blank=True,
        help_text=("Name of directory where static files for the article are"
                   "stored.")
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        output = "[" + str(self.id) + "] " + self.title + " by " + self.author
        return output

    def url(self):
        return "/article/" + str(self.id) + "/" + slugify(self.title)

    @property
    def preview(self):
        return os.path.join(STATIC_URL, self.path(), "preview.png")

    def search(p):
        qs = Article.objects.filter(published=PUBLISHED_ARTICLE)

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
