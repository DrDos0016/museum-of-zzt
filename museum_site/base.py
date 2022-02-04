from django.db import models

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

    def as_block(self):
        return "AB"

    def as_detailed_block(self):
        return "AB"

    def as_list_block(self):
        return "X"

    def as_gallery_block(self):
        return "X"

    def table_header(self):
        row = ""
        for f in self.table_fields:
            row += "<th>{}</th>".format(f)
        return "<tr>" + row + "</tr>"

    def scrub(self):
        return "X"




    class Meta:
        abstract = True
