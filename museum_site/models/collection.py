import os

from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.safestring import mark_safe

from museum_site.models.base import BaseModel
from museum_site.templatetags.zzt_tags import char


class Collection(BaseModel):
    """ Representation of a group of files with custom descriptions """
    model_name = "Collection"
    table_fields = ["Title"]
    sort_options = [
        {"text": "Newest", "val": "-modified"},
        {"text": "Oldest", "val": "modified"},
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
    ]
    sort_keys = {
        # Key - Value from <select> used in GET params
        # Value - Django order_by param
        "title": "title",
        "author": "user__username",
        "modified": "modified",
        "-modified": "-modified",
        "id": "id",
        "-id": "-id",
    }
    supported_views = ["detailed"]

    # Visibilities
    REMOVED = 0
    PRIVATE = 1
    UNLISTED = 2
    PUBLIC = 3
    VISIBILITY_CHOICES = [
        (REMOVED, "Removed"),
        (PRIVATE, "Private"),
        (UNLISTED, "Unlisted"),
        (PUBLIC, "Public"),
    ]

    # Fields
    title = models.CharField(max_length=120, db_index=True, help_text="The name of your collection. Used to generate URL for collection.")
    slug = models.SlugField(max_length=80, db_index=True, unique=True, editable=False, help_text="Unique idenifier for collection")
    description = models.TextField(help_text="Description of collection. Markdown supported.", blank=True, default="")
    visibility = models.IntegerField(
        default=PRIVATE,
        choices=VISIBILITY_CHOICES,
        help_text="Permissions to access your collection. Collections with no items contained will not be displayed even if they are marked public."
    )
    created = models.DateField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    item_count = models.IntegerField(default=0, editable=False)
    short_description = models.CharField(
        max_length=250,
        help_text="A short description of the collection displayed when browsing collections and not their contents. Plain text only.",
        blank=True,
        default=""
    )
    preview_image = models.ForeignKey("File", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")

    # Associations
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    contents = models.ManyToManyField("File", through="Collection_Entry")

    class Meta:
        ordering = ["-modified"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Set the slug
        self.slug = slugify(self.title)
        super(Collection, self).save(*args, **kwargs)

    def url(self):
        return reverse("view_collection", kwargs={"slug": self.slug})

    def preview_url(self):
        if self.preview_image:
            return self.preview_image.preview_url()
        return "/static/images/screenshots/no_screenshot.png"

    def belongs_to(self, user_id):
        if self.user.id == user_id:
            return True
        return False

    @property
    def visibility_str(self):
        return self.VISIBILITY_CHOICES[self.visibility][1]

    @mark_safe
    def author_link(self):
        if self.user:
            link = '{} <a href="{}">{}</a>'.format(
                char(
                    self.user.profile.char, self.user.profile.fg,
                    self.user.profile.bg, scale=2
                ),
                self.user.profile.link(),
                self.user.username
            )
        else:
            link = "Anonymous"

        return link

    def detailed_block_context(self, extras=None, *args, **kwargs):
        context = self.initial_context(*args, **kwargs)

        context["title"] = {"datum": "title", "value": self.title, "url": self.url()}
        context["slug"] = self.slug
        context["columns"] = []

        yours = False
        if self.user and context["request"]:
            yours = self.belongs_to(context["request"].user.id)

        context["columns"].append([
            {"datum": "text", "label": "Author", "value": self.author_link},
            {"datum": "text", "label": "Created", "value": self.created},
            {"datum": "text", "label": "Last Modified", "value": self.modified},
            {"datum": "text", "label": "Items In Collection", "value": str(self.item_count)},
            {"datum": "text", "label": "Short Description", "value": self.short_description or mark_safe("<i>None</i>")},
        ])

        if yours:
            context["links"] = True
            context["columns"][0].insert(0, {"datum": "text", "label": "Visibility", "value": self.visibility_str})
        return context


class Collection_Entry(models.Model):
    sort_options = [
        {"text": "Collection Order", "val": "canonical"},
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
        {"text": "Company", "val": "company"},
        {"text": "Rating", "val": "rating"},
        {"text": "Release Date (Newest)", "val": "-release"},
        {"text": "Release Date (Oldest)", "val": "release"},
    ]
    sort_keys = {
        # Key - Value from <select> used in GET params
        # Value - Django order_by param
        "canonical": "order",
        "title": "zfile__sort_title",
        "author": "zfile__author",
        "company": "zfile__company",
        "rating": "-zfile__rating",
        "release": "zfile__release_date",
        "-release": "-zfile__release_date",
        "id": "id",
        "-id": "-id",
    }

    collection = models.ForeignKey("Collection", on_delete=models.CASCADE, blank=True, null=True)
    zfile = models.ForeignKey("File", on_delete=models.SET_NULL, blank=True, null=True)
    collection_description = models.TextField(help_text="Optional description for the file as part of the collection. Markdown supported.", blank=True, default="")
    order = models.IntegerField(default=1, db_index=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return "Collection Entry #{} - [{}]".format(self.pk, self.zfile.title)
