import os

from django.db import models
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from museum.settings import STATIC_URL
from museum_site.constants import STATIC_PATH
from museum_site.core.misc import epoch_to_unknown
from museum_site.models.base import BaseModel
from museum_site.querysets.series_querysets import Series_Queryset


class Series(BaseModel):
    objects = Series_Queryset.as_manager()
    model_name = "Series"
    table_fields = ["Series", "Updated", "Latest", "First", "Total"]
    sort_options = [
        {"text": "Newest Entry", "val": "latest"},
        {"text": "Title", "val": "title"}
    ]
    sort_keys = {
        # Key - Value from <select> used in GET params
        # Value - Django order_by param
        "title": ["title"],
        "latest": ["-last_entry_date", "title"],
        "id": ["id"],
        "-id": ["-id"],
    }

    # Constants
    PREVIEW_DIRECTORY = os.path.join("pages/series-directory/")
    PREVIEW_DIRECTORY_FULL_PATH = os.path.join(
        STATIC_PATH, "pages/series-directory/"
    )

    # Fields
    title = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, editable=False)
    description = models.TextField(default="")
    preview = models.CharField(max_length=80, default="", blank=True)
    first_entry_date = models.DateField()
    last_entry_date = models.DateField()
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        if self.id:
            article_set = self.article_set.all()
            if article_set:
                self.first_entry_date = (
                    article_set.order_by("publish_date").first().publish_date
                )
                self.last_entry_date = (
                    article_set.order_by("publish_date").last().publish_date
                )
        else:
            self.first_entry_date = "1970-01-01"
            self.last_entry_date = "1970-01-01"

        # Prevent blank preview URLs
        if not self.preview:
            self.preview = self.slug + ".png"
        super(Series, self).save(*args, **kwargs)

    def url(self):
        return "/series/{}/{}/".format(self.id, self.slug)

    def preview_url(self):
        return os.path.join(self.PREVIEW_DIRECTORY, self.preview)

    def get_meta_tag_context(self):
        """ Returns a dict of keys and values for <meta> tags  """
        tags = {}
        tags["author"] = ["name", ""]
        tags["description"] = ["name", self.description]
        tags["og:title"] = ["property", self.title + " - Museum of ZZT"]
        tags["og:image"] = ["property", self.preview_url()]  # Domain and static path to be added elsewhere
        return tags


    def get_field_view(self, view="detailed"):
        return {"value": "<a href='{}'>{}</a>".format(self.url(), self.title), "safe": True}

    def get_field_last_updated(self, view="detailed"):
        article = self.article_set.all().order_by("-publish_date").first()
        return {"label": "Last Updated", "value": self.last_entry_date}

    def get_field_latest_article(self, view="detailed"):
        article = self.article_set.all().order_by("-publish_date").first()
        if view == "list" or view == "gallery":
            value = "<a href='{}'>{}</a>".format(article.url(), "Latest")
        else:
            value = "<a href='{}'>{}</a>".format(article.url(), article.title)
        return {"label": "Latest Article", "value": value, "safe": True}

    def get_field_first_article(self, view="detailed"):
        article = self.article_set.all().order_by("publish_date").first()
        if view == "list" or view == "gallery":
            value = "<a href='{}'>{}</a>".format(article.url(), "First")
        else:
            value = "<a href='{}'>{}</a>".format(article.url(), article.title)
        return {"label": "First Article", "value": value, "safe": True}

    def get_field_total_articles(self, view="detailed"):
        return {"label": "Total Articles", "value": self.article_set.count()}

    def get_field_description(self, view="detailed"):
        return {"label": "Description", "value": self.description}

    def context_detailed(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "detailed"]
        context["columns"] = []

        columns = [
            ["last_updated", "latest_article", "first_article", "total_articles", "description"],
        ]

        for col in columns:
            column_fields = []
            for field_name in col:
                field_context = self.get_field(field_name)
                column_fields.append(field_context)
            context["columns"].append(column_fields)
        return context

    def context_list(self):
        context = self.context_universal()
        context["roles"] = ["list"]
        context["cells"] = []

        cell_list = ["view", "last_updated", "latest_article", "first_article", "total_articles"]
        for field_name in cell_list:
            cell_fields = self.get_field(field_name, view="list")
            context["cells"].append(cell_fields)
        return context

    def context_gallery(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "gallery"]
        context["fields"] = [
            self.get_field("latest_article", view="gallery"),
            self.get_field("first_article", view="gallery"),
        ]
        return context
