from django.template.defaultfilters import slugify
from django.urls import reverse

from museum_site.models.base import BaseModel


class Custom_Block(BaseModel):
    model_name = "Custom Block"
    key = ""
    pk = "X"

    def url(self):
        return "CUSTOM URL"

    def get_absolute_url(self):
        return "CUSTOM URL"

    def preview_url(self):
        return self.custom_context["preview"]["url"]


class Article_Category_Block(Custom_Block):
    """ Faux Detailed Block used for listing article categories on Articles By Category page """
    model_name = "Article Category"

    def get_field_view(self, view="detailed"):
        url = reverse("article_browse_category", kwargs={"category_slug": slugify(self.custom_context["title"])})
        texts = {
            "detailed": "View Contents", "list": self.custom_context["title"], "gallery": self.custom_context["title"], "title": self.custom_context["title"]
        }
        text = texts[view]
        return {"value": "<a href='{}'>{}</a>".format(url, text), "safe": True}

    def get_field_article_count(self, view="detailed"):
        return {"label": "Number of Articles", "value": self.custom_context["article_count"]}

    def get_field_article_date(self, view="detailed"):
        return {"label": "Published", "value": self.custom_context["article_date"]}

    def get_field_latest(self, view="detailed"):
        return {
            "label": "Latest", "value": "<a href='{}'>{}</a>".format(self.custom_context["latest"]["url"], self.custom_context["latest"]["value"]), "safe": True
        }

    def get_field_description(self, view="detailed"):
        return {"label": "Description", "value": self.custom_context["description"], "safe": True}

    def set_initial_attributes(self, context={}):
        """ Runs outside of model_block flow. Must be executed manually prior to template rendering """
        self.custom_context = context

    def context_detailed(self):
        context = self.context_universal()
        context["columns"] = []

        columns = [
            ["article_count", "latest", "article_date", "description"],
        ]

        for col in columns:
            column_fields = []
            for field_name in col:
                field_context = self.get_field(field_name)
                column_fields.append(field_context)
            context["columns"].append(column_fields)
        return context

class Faux_Detailed_Block(Custom_Block):
    """ Faux Detailed Block used for linking to other sites while emulating the look of a Musuem ZFile (see pub pack Vol. 9) """
    model_name = "Faux Block"
