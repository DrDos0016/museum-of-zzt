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

    def url(self):
        raise NotImplementedError('Subclasses must implement "url" method.')

    def preview_url(self):
        raise NotImplementedError(
            'Subclasses must implement "preview_url" method.'
        )

    def scrub(self):
        raise NotImplementedError(
            'Subclasses must implement "scrub" method.'
        )

    def get_all_icons(self, **kwargs):
        # Stub
        return []

    def get_major_icons(self, **kwargs):
        # Stub
        return []

    def initial_context(self, *args, **kwargs):
        context = {
            "pk": self.pk,
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


    class Meta:
        abstract = True
