from django.template.defaultfilters import slugify

from museum_site.models.base import BaseModel


class Custom_Block(BaseModel):
    model_name = "Custom Block"
    key = ""
    pk = "X"

    def url(self):
        return "CUSTOM URL"

    def preview_url(self):
        return self.custom_context["preview"]["url"]


class Article_Category_Block(Custom_Block):
    model_name = "Article Category"

    def get_field_view(self, view="detailed"):
        url = "/article/category/{}/".format(slugify(self.custom_context["title"]))
        texts = {
            "detailed": "View Contents", "list": self.custom_context["title"], "gallery": self.custom_context["title"], "title": self.custom_context["title"]
        }
        text = texts[view]
        return {"value": "<a href='{}'>{}</a>".format(url, text), "safe": True}

    def get_field_article_count(self, view="detailed"):
        return {"label": "Number of Articles", "value": self.custom_context["article_count"]}

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
            ["article_count", "latest", "description"],
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