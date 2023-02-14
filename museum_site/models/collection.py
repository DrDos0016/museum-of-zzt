from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.safestring import mark_safe

from museum_site.models.base import BaseModel
from museum_site.querysets.collection_querysets import *


class Collection(BaseModel):
    """ Representation of a group of files with custom descriptions """
    objects = Collection_Queryset.as_manager()
    model_name = "Collection"
    cell_list = ["view", "author", "modified", "item_count", "short_description"]
    guide_word_values = {"id": "pk", "title": "title", "author": "author", "modified": "modified"}
    to_init = ["yours"]
    is_yours = False
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
        return "images/screenshots/no_screenshot.png"

    @property
    def visibility_str(self):
        return self.VISIBILITY_CHOICES[self.visibility][1]

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

    def get_field_visibility(self, view="detailed"):
        return {"label": "Visibility", "value": self.visibility_str}

    def get_field_edit_collection(self, view="detailed"):
        return {"value": "<a href='/collection/edit/{}/'>Edit Collection</a>".format(self.slug), "safe": True}

    def get_field_manage_contents(self, view="detailed"):
        return {"value": "<a href='/collection/manage-contents/{}/'>Manage Collection Contents</a>".format(self.slug), "safe": True}

    def get_field_delete(self, view="detailed"):
        return {"value": "<a href='/collection/delete/{}/'>Delete Collection</a>".format(self.slug), "safe": True}

    def get_field(self, field_name, view="detailed"):
        if hasattr(self, "get_field_{}".format(field_name)):
            field_context = getattr(self, "get_field_{}".format(field_name))(view)
        else:
            field_context = {"label": field_name, "value": "placeholder"}
        return field_context

    def context_detailed(self):
        context = self.context_universal()
        context["roles"] = self.roles
        context["columns"] = []

        columns = [
            ["author", "created", "modified", "item_count", "short_description"]
        ]

        if self.is_yours:
            columns[0].append("visibility")

        for col in columns:
            column_fields = []
            for field_name in col:
                field_context = self.get_field(field_name)
                column_fields.append(field_context)
            context["columns"].append(column_fields)

        if self.is_yours:
            context["show_actions"] = True
            action_list = ["edit_collection", "manage_contents", "delete"]
            actions = []
            for action in action_list:
                actions.append(self.get_field(action, view="detailed"))
            context["actions"] = actions
        else:
            context["show_actions"] = False

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
            self.get_field("author", view="gallery"),
            self.get_field("item_count", view="gallery")
        ]
        return context

    def _init_yours(self):
        """ Determine if the collection is "yours" """
        self.is_yours = False
        if self.request:
            self.is_yours = True if self.request.user.pk == self.user.pk else False

    def _init_roles(self, view):
        super()._init_roles(view)

        if self.visibility == self.PRIVATE:
            self.roles.append("private")
        elif self.visibility == self.UNLISTED:
            self.roles.append("unlisted")

    def get_guideword_modified(self): return self.modified.strftime("%b %d, %Y")
    def get_guideword_author(self): return self.user.username



class Collection_Entry(BaseModel):
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

    guide_word_values = {"id": "pk", "title": "title", "author": "author", "company": "company", "rating": "rating", "release": "release_date"}

    supported_views = ["detailed"]
    model_name = "Collection Entry"
    to_init = ["zfile"]
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

    def get_field(self, field_name, view="detailed"):
        if hasattr(self, "get_field_{}".format(field_name)):
            field_context = getattr(self, "get_field_{}".format(field_name))(view)
        elif self.zfile is not None and hasattr(self.zfile, "get_field_{}".format(field_name)):
            field_context = getattr(self.zfile, "get_field_{}".format(field_name))(view)
        else:
            field_context = {"label": field_name, "value": "placeholder"}
        return field_context

    def context_detailed(self):
        if not self.zfile:
            return {}

        context = self.zfile.context
        context["roles"] = ["model-block", "detailed", "collection-content"]
        context["collection_description"] = self.collection_description
        if self.zfile.extras:
            context["extras"] = self.zfile.extras
        return context

    def _init_zfile(self):
        if self.zfile:
            self.zfile.init_model_block_context("detailed", self.request, self.show_staff)

    def get_guideword_title(self): return self.zfile.get_guideword_title()
    def get_guideword_author(self): return self.zfile.get_guideword_author()
    def get_guideword_company(self): return self.zfile.get_guideword_company()
    def get_guideword_rating(self): return self.zfile.get_guideword_rating()
    def get_guideword_release_date(self): return self.zfile.get_guideword_release_date()
    def get_guideword_canonical(self): return self.zfile.get_guideword_title()  # Deliberate
