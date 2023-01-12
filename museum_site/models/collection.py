from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.safestring import mark_safe

from museum_site.models.base import BaseModel
from museum_site.querysets.collection_querysets import *
from museum_site.templatetags.zzt_tags import char


class Collection(BaseModel):
    """ Representation of a group of files with custom descriptions """
    objects = Collection_Queryset.as_manager()
    model_name = "Collection"
    table_fields = ["Title", "Author", "Last Modified", "Items", "Short Desc."]
    sort_options = [
        {"text": "Newest", "val": "-modified"},
        {"text": "Oldest", "val": "modified"},
        {"text": "Title", "val": "title"},
        {"text": "Author", "val": "author"},
    ]
    sort_keys = {
        # Key - Value from <select> used in GET params
        # Value - Django order_by param
        "title": ["title"],
        "author": ["user__username", "title"],
        "modified": ["modified", "title"],
        "-modified": ["-modified", "title"],
        "id": ["id"],
        "-id": ["-id"],
    }
    #supported_views = ["detailed", "list", "gallery"]
    supported_views = ["detailed"]

    # Visibilities
    REMOVED = 0
    PRIVATE = 1
    UNLISTED = 2
    PUBLIC = 3
    VISIBILITY_CHOICES = [
        (REMOVED, "Removed"),  # TODO: Not implemented
        (PRIVATE, "Private"),
        (UNLISTED, "Unlisted"),
        (PUBLIC, "Public"),
    ]

    SORT_CHOICES = [
        ("manual", "Manual Order"),
        ("title", "Title"),
        ("author", "Author"),
        ("company", "Company"),
        ("rating", "Rating"),
        ("release", "Release Date (Newest)"),
        ("-release", "Release Date (Oldest)"),
    ]

    # Fields
    title = models.CharField(max_length=120, db_index=True, help_text="The name of your collection. Used to generate URL for collection.")
    slug = models.SlugField(max_length=80, db_index=True, unique=True, editable=False, help_text="Unique idenifier for collection")
    description = models.TextField(help_text="Description of collection. Markdown supported.", blank=True, default="")
    visibility = models.IntegerField(
        default=PRIVATE,
        choices=VISIBILITY_CHOICES,
        help_text="Permissions to access your collection. Collections with any associated files will not be displayed even if they are marked public."
    )
    created = models.DateField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    item_count = models.IntegerField(default=0, editable=False)
    short_description = models.CharField(
        max_length=250,
        help_text="A short description of the collection displayed when browsing collections. Plain text only.",
        blank=True,
        default=""
    )
    preview_image = models.ForeignKey("File", on_delete=models.SET_NULL, null=True, blank=True, related_name="+")
    default_sort = models.CharField(
        max_length=20, choices=SORT_CHOICES, default="manual",
        help_text=(
            'The default sorting method when viewing this collection\'s contents. '
            'Set to "Manual Order" to display contents in an arbitrary order of your choosing.'
        ),
    )

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
        return reverse("view_collection", kwargs={"collection_slug": self.slug})

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
            if self.visibility_str != "Public":
                context["roles"].append(self.visibility_str.lower())
        return context

    def get_meta_tag_context(self):
        """ Returns a dict of keys and values for <meta> tags  """
        tags = {}
        tags["author"] = ["name", self.user.username]
        tags["description"] = ["name", '"{}" a collection by {}.'.format(self.title, self.user.username)]

        tags["og:title"] = ["property", self.title + " - Museum of ZZT"]
        tags["og:image"] = ["property", self.preview_url()]  # Domain and static path to be added elsewhere
        return tags

    def get_field_view(self, view="detailed"):
        return {"value": "<a href='{}'>{}</a>".format(self.url(), self.title), "safe": True}

    def get_field_author(self, view="detailed"):
        return {"label": "Author", "value": self.author_link()}

    def get_field_created(self, view="detailed"):
        return {"label": "Created", "value": self.created}

    def get_field_modified(self, view="detailed"):
        return {"label": "Last Modified", "value": self.modified}

    def get_field_item_count(self, view="detailed"):
        if view == "gallery":
            return {"label": "Items In Collection", "value": str(self.item_count) + " items"}
        return {"label": "Items In Collection", "value": self.item_count}

    def get_field_short_description(self, view="detailed"):
        return {"label": "Short Description", "value": self.short_description}

    def get_field(self, field_name, view="detailed"):
        if hasattr(self, "get_field_{}".format(field_name)):
            field_context = getattr(self, "get_field_{}".format(field_name))(view)
        else:
            field_context = {"label": field_name, "value": "placeholder"}
        return field_context

    def context_universal(self):
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
        context["show_actions"] = True
        context["columns"] = []

        columns = [
            ["author", "created", "modified", "item_count", "short_description"]
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

        cell_list = ["view", "author", "modified", "item_count", "short_description"]
        for field_name in cell_list:
            cell_fields = self.get_field(field_name, view="list")
            context["cells"].append(cell_fields)
        return context

    def context_gallery(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "gallery"]
        context["fields"] = [
            self.get_field("author", view="gallery"),
            self.get_field("item_count", view="gallery")
        ]
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
        "canonical": ["order"],
        "title": ["zfile__sort_title"],
        "author": ["zfile__authors__title", "zfile__sort_title"],
        "company": ["zfile__companies__title", "zfile__sort_title"],
        "rating": ["-zfile__rating"],
        "release": ["zfile__release_date", "zfile__sort_title"],
        "-release": ["-zfile__release_date", "zfile__sort_title"],
        "id": ["id"],
        "-id": ["-id"],
    }

    supported_views = ["detailed"]
    model_name = "Collection Entry"
    objects = Collection_Entry_Queryset.as_manager()

    collection = models.ForeignKey("Collection", on_delete=models.CASCADE, blank=True, null=True)
    zfile = models.ForeignKey("File", on_delete=models.SET_NULL, blank=True, null=True)
    collection_description = models.TextField(
        help_text="Optional description for the file as part of the collection. Markdown supported.",
        blank=True, default=""
    )
    order = models.IntegerField(default=1, db_index=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return "Collection Entry #{} - [{}]".format(self.pk, self.zfile.title)

    def url(self):
        return self.zfile.url() if self.zfile is not None else "images/screenshots/no_screenshot.png"

    def preview_url(self):
        return self.zfile.preview_url() if self.zfile is not None else "#"

    def detailed_block_context(self, request=None):
        if self.zfile is not None:
            context = self.zfile.detailed_collection_block_context(collection_description=self.collection_description)
        else:
            context = {}
        return context

    def get_field(self, field_name, view="detailed"):
        if hasattr(self, "get_field_{}".format(field_name)):
            field_context = getattr(self, "get_field_{}".format(field_name))(view)
        elif self.zfile is not None and hasattr(self.zfile, "get_field_{}".format(field_name)):
            field_context = getattr(self.zfile, "get_field_{}".format(field_name))(view)
        else:
            field_context = {"label": field_name, "value": "placeholder"}
        return field_context

    def context_universal(self):
        if self.zfile is not None:
            self.zfile.init_actions()

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
        context["show_actions"] = True
        context["columns"] = []

        columns = [
            ["authors", "companies", "zfile_date", "genres", "filename", "size"],
            ["details", "rating", "boards", "language", "publish_date"],
        ]

        for col in columns:
            column_fields = []
            for field_name in col:
                field_context = self.get_field(field_name)
                column_fields.append(field_context)
            context["columns"].append(column_fields)

        action_list = ["download", "play", "view", "review", "article", "attributes"]
        actions = []
        for action in action_list:
            actions.append(self.get_field(action, view="detailed"))

        context["actions"] = actions

        return context

    def context_list(self):
        context = self.context_universal()
        context["roles"] = ["list"]
        context["cells"] = []

        cell_list = ["download", "view", "authors", "companies", "genres", "zfile_date", "rating"]
        for field_name in cell_list:
            cell_fields = self.get_field(field_name, view="list")
            context["cells"].append(cell_fields)
        return context

    def context_gallery(self):
        context = self.context_universal()
        context["roles"] = ["model-block", "gallery"]
        context["fields"] = [
            self.get_field("authors", view="gallery")
        ]
        return context

    def table_header(self):
        if self.zfile:
            return self.zfile.table_header()
        else:
            return "<th>ERROR</th>"
