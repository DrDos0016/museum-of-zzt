from django.db import models
from django.utils.safestring import mark_safe


class BaseModel(models.Model):
    model_name = None
    table_fields = []
    supported_views = ["detailed", "list", "gallery"]
    extra_context = {}

    def admin_url(self):
        name = self.model_name.replace("-", "_").lower()
        return "/admin/museum_site/{}/{}/change/".format(name, self.id)

    def _init_icons(self):
        # Stub
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

    class Meta:
        abstract = True
