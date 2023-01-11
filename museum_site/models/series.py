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

    def detailed_block_context(self, *args, **kwargs):
        """ Return info to populate a detail block """
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title={"datum": "title", "value": self.title, "url": self.url},
            columns=[],
        )

        context["columns"].append([
            {"datum": "text", "label": "Newest Entry", "value": self.last_entry_date},
            {"datum": "text", "label": "Oldest Entry", "value": epoch_to_unknown(self.first_entry_date)},
            {"datum": "text", "label": "Articles", "value": self.article_set.count()},
            {"datum": "text", "value": mark_safe("<p>{}</p>".format(self.description))},
        ])

        return context

    def list_block_context(self, *args, **kwargs):
        context = dict(
            pk=self.pk,
            model=self.model_name,
            url=self.url,
            cells=[
                {"datum": "link", "url": self.url(), "value": self.title, "tag": "td"},
                {"datum": "text", "value": self.last_entry_date, "tag": "td"},
                {"datum": "text", "value": epoch_to_unknown(self.last_entry_date), "tag": "td"},
                {"datum": "text", "value": epoch_to_unknown(self.first_entry_date), "tag": "td"},
                {"datum": "text", "value": self.article_set.count(), "tag": "td"},
            ],
        )

        return context

    def gallery_block_context(self, *args, **kwargs):
        context = dict(
            pk=self.pk,
            model=self.model_name,
            preview=dict(url=self.preview_url, alt=self.preview_url),
            url=self.url,
            title={"datum": "title", "url": self.url(), "value": self.title},
            columns=[],
        )

        context["columns"].append([
            {"datum": "text", "value": self.last_entry_date}
        ])

        return context

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
            value = "<a href='{}'>{}</a>".format(self.url(), "Latest")
        else:
            value = "<a href='{}'>{}</a>".format(self.url(), article.title)
        return {"label": "Latest Article", "value": value, "safe": True}

    def get_field_first_article(self, view="detailed"):
        article = self.article_set.all().order_by("publish_date").first()
        if view == "list" or view == "gallery":
            value = "<a href='{}'>{}</a>".format(self.url(), "First")
        else:
            value = "<a href='{}'>{}</a>".format(self.url(), article.title)
        return {"label": "Latest Article", "value": value, "safe": True}

    def get_field_total_articles(self, view="detailed"):
        return {"label": "Total Articles", "value": self.article_set.count()}

    def get_field_description(self, view="detailed"):
        return {"label": "Description", "value": self.description}

    def get_field(self, field_name, view="detailed"):
        if hasattr(self, "get_field_{}".format(field_name)):
            field_context = getattr(self, "get_field_{}".format(field_name))(view)
        else:
            field_context = {"label": field_name, "value": "placeholder"}
        return field_context

    def context_universal(self):
        self.get_all_icons()
        context = {
            "model": self.model_name,
            "pk": self.pk,
            "model_key": self.key if hasattr(self, "key") else self.pk,
            "url": self.url(),
            "preview": {
                "no_zoom": False,
                "zoomed": False,
                "url": self.preview_url,
                "alt": self.preview_url,
            },
            "title": self.get_field("view", view="title"),
        }
        return context

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
