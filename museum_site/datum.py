from django.template.loader import render_to_string


class Datum(object):
    def __init__(self, context):
        self.context = context
        return

    def render(self):
        return render_to_string(self.template_name, self.context)

    __str__ = render


class TextDatum(Datum):
    template_name = "museum_site/datum/text-datum.html"

    def __init__(self, *args, **kwargs):
        super().__init__(kwargs)


class LinkDatum(Datum):
    template_name = "museum_site/datum/link-datum.html"

    def __init__(self, *args, **kwargs):
        if "url" not in kwargs:
            raise Exception("Link Datum requires a URL parameter")
        super().__init__(kwargs)


class CellDatum(Datum):
    template_name = "museum_site/datum/cell-datum.html"

    def __init__(self, *args, **kwargs):
        super().__init__(kwargs)
