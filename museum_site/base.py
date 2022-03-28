from django.db import models
from django.utils.safestring import mark_safe


class BaseModel(models.Model):
    model_name = None
    table_fields = []
    supported_views = ["detailed", "list", "gallery"]

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

    class Meta:
        abstract = True
