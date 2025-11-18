from django.db import models
from django.utils.safestring import mark_safe

from museum_site.templatetags.zzt_tags import char


class BaseModel(models.Model):
    model_name = None
    to_init = []
    table_fields = []
    cell_list = []
    supported_views = ["detailed", "list", "gallery"]
    has_icons = False  # Updated from class specific obj._init_icons()
    actions = {}
    show_actions = False
    context = {}
    extras = []
    detail_ids = []
    roles = []
    request = None
    show_staff = False
    guide_word_values = {}

    DEBUG_PRINT = False

    class Meta:
        abstract = True

    def admin_url(self):
        name = self.model_name.replace("-", "_").lower()
        return "/admin/museum_site/{}/{}/change/".format(name, self.id)

    @property
    def model_key(self):
        return self.key if hasattr(self, "key") else self.pk

    def dprint(self, *args, **kwargs):
        if self.DEBUG_PRINT:
            print(*args, **kwargs)
        return False

    def _init_actions(self): self.actions = {}
    def _init_detail_ids(self): self.detail_ids = []
    def _init_extras(self): self.extras = []

    def _init_roles(self, view):
        self.roles = []
        if view != "list":  # List views just use table rows instead of a lot of alternate CSS rules
            self.roles.append("model-block")
        self.roles.append(view)

    def _init_icons(self):
        self._minor_icons = []
        self._major_icons = []

    def get_all_icons(self):
        # Returns combined list of both major and minor icons, populating if needed
        if not hasattr(self, "_major_icons"):
            self._init_icons()
        return self._major_icons + self._minor_icons

    def get_major_icons(self):
        # Returns list of major icons, populating if needed
        if not hasattr(self, "_major_icons"):
            self._init_icons()
        return self._major_icons

    def get_related_list(self, obj, field=None):
        """ Get all associated instances of related object OBJ and return them in a list. Optionally filter only to a specified FIELD """
        output = []
        if hasattr(self, obj):
            qs = getattr(self, obj).all()
            for i in qs:
                if field is None:
                    output.append(i)
                else:
                    output.append(getattr(i, field))
        return output

    @mark_safe
    def table_header(self):
        row = ""
        for i in getattr(self, "table_fields"):
            row += "<th>{}</th>".format(i)
        return "<tr>" + row + "</tr>"

    @mark_safe
    def author_link(self, default_name="Anonymous"):
        """ Return HTML link to author profile if a user is found, otherwise use an author field if it exists, otherwise a default value """
        if self.user:
            link = '{} <a href="{}">{}</a>'.format(
                char(self.user.profile.char, self.user.profile.fg, self.user.profile.bg, scale=2),
                self.user.profile.get_absolute_url(),
                self.user.username
            )
        elif hasattr(self, "author") and self.author:
            link = self.author
        else:
            link = default_name
        return link

    # 2023 Model Blocks
    def init_model_block_context(self, view="detailed", request=None, *args, **kwargs):
        """ Entry point for 2023 Model Blocks """
        self.dprint("INIT MODEL BLOCK CONTEXT")
        self.request = request
        self.context = {}
        if request:
            self.show_staff = request.user.is_staff
        self._init_roles(view)  # Every model has roles (also used as CSS classes)
        for init_func in self.to_init:  # Initialize the object
            getattr(self, "_init_{}".format(init_func))()
        self.context.update(self.context_universal())
        # Update with view-specific context
        self.context.update(getattr(self, "context_{}".format(view))())
        # Update with extras
        if self.extras:
            self.context.update(self.context_extras())
        # Update with kwargs
        if kwargs:
            self.process_kwargs(kwargs)

    def get_field(self, field_name, view="detailed"):
        print("Getting field", field_name, view, "::::", self.title)
        if hasattr(self, "get_field_{}".format(field_name)):
            field_context = getattr(self, "get_field_{}".format(field_name))(view)
        else:
            field_context = {"label": field_name, "value": "placeholder"}

        if field_context:
            field_context["field_name"] = field_name
        return field_context

    def get_field_edit(self, view="detailed"):
        return {"label": "Edit", "value": "<a href='{}'>Edit {} #{}</a>".format(self.admin_url(), self.model_name, self.pk), "safe": True}

    def context_universal(self, request=None):
        context = {
            "model": self.model_name,
            "pk": self.pk,
            "model_key": self.model_key,
            "url": self.get_absolute_url(),
            "roles": self.roles,
            "preview": {
                "no_zoom": False,
                "zoomed": self.model_name == "WoZZT-Queue",  # WoZZT Queue is the only one pre-zoomed
                "url": self.preview_url,
                "alt": self.preview_url,
            },
            "title": self.get_field("view", view="title"),
            "extras": self.extras,
            "request": self.request,
            "admin_url": self.admin_url(),
        }
        return context

    def context_detailed(self): return {}
    def context_list(self): return {}
    def context_gallery(self): return {}
    def context_extras(self): return {}
    def process_kwargs(self, kwargs=None): return None

    def prepare_icons_for_field(self, kind="all"):
        if self.has_icons:
            icons = "<div class='model-block-icons'>"
            for icon in getattr(self, "get_{}_icons".format(kind))():
                icons += '<span class="icon {}" title="{}">{}</span>'.format(icon["role"], icon["title"], icon["glyph"])
            return icons + "</div>"
        return ""

    def guide_words(self, sort):
        if sort:
            sort = sort.replace("-", "")  # Strip reverse sign
        attr = self.guide_word_values.get(sort, "title")
        value = getattr(self, "get_guideword_{}".format(attr))()
        if self.model_name != "Collection Entry":
            return (self.model_key, value)
        else:
            return (self.zfile.model_key, value)

    def get_guideword_pk(self): return self.pk
    def get_guideword_title(self): return self.title

    def to_select(self):
        # Return a string representation of the object meant for user facing widgets
        return self.__str__()

    def field_context(self, label="", text="", icons=None, url="#", title="", safe=True, kind="link", clamped=False, target=""):
        icons_str = self.prepare_icons_for_field(kind=icons) if icons else ""
        if kind == "link":
            if target:
                target = " class='noext' target='{}'".format(target)
            value = "<a href='{}'{}>{}{}</a>".format(url, target, icons_str, text)
        elif kind == "faded":
            value = "<span class='faded'>{}<i>{}</i></span>".format(icons_str, text)
        elif kind == "text":
            value = text if not title else "<span title='{}'>{}</span>".format(title, text)

        context = {"label": label, "value": value, "safe": safe, "clamped": clamped}
        return context

    def get_field_data_for_columns(self, columns):
        output = []
        for col in columns:
            column_fields = []
            for field_name in col:
                field_context = self.get_field(field_name)
                column_fields.append(field_context)
            output.append(column_fields)
        return output

    def get_field_data_list(self, field_list, view="detailed"):
        output = []
        for field in field_list:
            output.append(self.get_field(field, view=view))
        return output

