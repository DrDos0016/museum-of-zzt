from django.db import models
from django.utils.safestring import mark_safe


class BaseModel(models.Model):
    model_name = None
    to_init = []
    table_fields = []
    supported_views = ["detailed", "list", "gallery"]
    has_icons = False  # Updated from class specific obj._init_icons()
    actions = {}
    context = {"X": "BaseModel Context"}
    extra_context = {}
    detail_ids = []


    def admin_url(self):
        name = self.model_name.replace("-", "_").lower()
        return "/admin/museum_site/{}/{}/change/".format(name, self.id)

    def _init_icons(self, request={}, show_staff=False):
        # Stub
        self._minor_icons = []
        self._major_icons = []

    def _init_actions(self, request={}, show_staff=False):
        # Stub
        self.actions = {}

    def _init_detail_ids(self, request={}, show_staff=False):
        # Stub
        self.detail_ids = []

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

    def initial_context(self, *args, **kwargs):
        context = {
            "pk": self.pk,
            "hash_id": "{}-{}".format(self.model_name.lower(), self.pk),
            "model": self.model_name,
            "preview": {"url": self.preview_url(), "alt": self.preview_url()},
            "url": self.url(),
            "icons": self.get_all_icons(),
            "major_icons": self.get_major_icons(),
            "roles": [],
            "debug": False,
            "request": None,
            "extras": [],
        }

        request = kwargs.get("request")
        context["request"] = request

        # Debug mode
        if request and request.session.get("DEBUG"):
            context["debug"] = True

        if hasattr(self, "extra_context"):
            context.update(self.extra_context)

        return context

    def ssv(self, field_name, field_attr="title"):
        # Get a string of slash separated values for a many-to-many field
        ssv = ""
        if hasattr(self, field_name):
            entries = list(
                getattr(self, field_name).all().values_list(
                    field_attr, flat=True
                )
            )
            ssv = "/".join(entries)
        return ssv

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
        for i in getattr(self, "table_fields", ["TABLE FIELDS ARE UNDEFINED"]):
            row += "<th>{}</th>".format(i)
        return "<tr>" + row + "</tr>"

    # 2023 Model Blocks
    def render_model_block(self, view="detailed", request={}, show_staff=False):
        for init_func in self.to_init:  # Initialize the object
            getattr(self, "_init_{}".format(init_func))(request, show_staff)
        self.context = self.context_universal()
        # Update with view-specific context
        self.context.update(getattr(self, "context_{}".format(view))())

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
                "zoomed": self.model_name == "WoZZT-Queue",  # WoZZT Queue is the only one
                "url": self.preview_url,
                "alt": self.preview_url,
            },
            "title": self.get_field("view", view="title"),
        }
        return context

    def context_detailed(self): return {}
    def context_list(self): return {}
    def context_gallery(self): return {}

    def prepare_icons_for_field(self):
        if self.has_icons:
            icons = "<div class='model-block-icons'>"
            for icon in self.get_all_icons():
                icons += '<span class="icon {}" title="{}">{}</span>'.format(icon["role"], icon["title"], icon["glyph"])
            return icons + "</div>"
        return ""

    class Meta:
        abstract = True
