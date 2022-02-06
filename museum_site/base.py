from django.db import models
from django.utils.safestring import mark_safe

class BaseModel(models.Model):
    model_name = None
    #title
    #description
    #preview
    #table_fields = []

    def admin_url(self):
        name = self.model_name.replace("-", "_").lower()
        return "/admin/museum_site/{}/{}/change/".format(name, self.id)

    def url(self):
        return "URL!"

    def preview_url(self):
        return "Preview url"

    def as_block(self, view="detailed", *args, **kwargs):
        return getattr(self, "as_{}_block".format(view))(*args, **kwargs)

    def as_detailed_block(self, *args, **kwargs):
        raise NotImplementedError('Subclasses must implement "as_detailed_block" method.')

    def as_list_block(self, *args, **kwargs):
        raise NotImplementedError('Subclasses must implement "as_list_block" this method.')

    def as_gallery_block(self, *args, **kwargs):
        raise NotImplementedError('Subclasses must implement "as_gallery_block" method.')

    @mark_safe
    def table_header(self, *args, **kwargs):
        row = ""
        for f in self.table_fields:
            row += "<th>{}</th>".format(f)
        return "<tr>" + row + "</tr>"


    def scrub(self):
        raise NotImplementedError('Subclasses must implement "scrub" method.')


    class Meta:
        abstract = True
