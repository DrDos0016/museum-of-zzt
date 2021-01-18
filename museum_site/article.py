from datetime import datetime

from django.db import models
from django.template.defaultfilters import slugify

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
    date            -- Date the article was written
    published       -- If the article is available to the public
    summary         -- Summary for Opengraph
    preview         -- Path to preview image
    allow_comments  -- Allow user comments on the article
    spotlight       -- Allow appearance on front page
    """
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    content = models.TextField(default="")
    css = models.TextField(default="", blank=True)
    schema = models.CharField(max_length=6, choices=ARTICLE_FORMATS)
    date = models.DateField(default="1970-01-01")
    published = models.IntegerField(
        default=UNPUBLISHED_ARTICLE,
        choices=ARTICLE_PUBLISH
    )
    summary = models.CharField(max_length=150, default="", blank=True)
    preview = models.CharField(max_length=80, default="", blank=True)
    allow_comments = models.BooleanField(default=False)
    spotlight = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        output = "[" + str(self.id) + "] " + self.title + " by " + self.author
        return output

    def url(self):
        return "/article/" + str(self.id) + "/" + slugify(self.title)
