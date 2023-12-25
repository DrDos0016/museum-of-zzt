import os

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.safestring import mark_safe

from museum.settings import STATIC_URL
from museum_site.constants import STATIC_PATH, DATE_HR
from museum_site.core.sorters import Series_Sorter
from museum_site.models.base import BaseModel
from museum_site.querysets.series_querysets import Series_Queryset


class Series(BaseModel):
    objects = Series_Queryset.as_manager()
    model_name = "Series"
    table_fields = ["Series", "Updated", "Latest", "First", "Total"]
    cell_list = ["view", "last_updated", "latest_article", "first_article", "total_articles"]
    guide_word_values = {"id": "pk", "latest": "latest", "title": "title"}
    sorter = Series_Sorter

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
    first_entry_date = models.DateField(null=True, blank=True)
    last_entry_date = models.DateField(null=True, blank=True)
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title

    def to_select(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        if self.id:
            article_set = self.article_set.all()
            if article_set:
                self.first_entry_date = article_set.order_by("publish_date").first().publish_date
                self.last_entry_date = article_set.order_by("publish_date").last().publish_date

        # Prevent blank preview URLs
        if not self.preview:
            self.preview = self.slug + ".png"
        super(Series, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("series_view", kwargs={"series_id": self.pk, "slug": self.slug})

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
        return {"value": "<a href='{}'>{}</a>".format(self.get_absolute_url(), self.title), "safe": True}

    def get_field_last_updated(self, view="detailed"):
        article = self.article_set.all().order_by("-publish_date").first()
        return {"label": "Last Updated", "value": self.last_entry_date}

    def get_field_latest_article(self, view="detailed"):
        article = self.article_set.all().order_by("-publish_date").first()
        return self.get_field_this_article(article, view, label="Latest")

    def get_field_first_article(self, view="detailed"):
        article = self.article_set.all().order_by("publish_date").first()
        return self.get_field_this_article(article, view, label="First")

    def get_field_this_article(self, article, view="detailed", label="?"):
        article.request = self.request
        article._init_access_level()
        article._init_icons()
        if view == "list" or view == "gallery":
            field = article.get_field_view("title", text_override=label)
        else:
            field = article.get_field_view("title")
        field["label"] = "{} Article".format(label)
        return field

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

        for field_name in self.cell_list:
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

    def get_guideword_latest(self): return self.last_entry_date.strftime(DATE_HR)
