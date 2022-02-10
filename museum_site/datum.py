from django.template.loader import render_to_string


class Datum(object):
    def __init__(self, context, **kwargs):
        self.context = context
        return

    def render(self):
        return render_to_string(self.template_name, self.context)

    __str__ = render


class TextDatum(Datum):
    template_name = "museum_site/datum/text-datum.html"

    def __init__(self, *args, **kwargs):
        super().__init__(kwargs)


class StubDatum(TextDatum):
    def render(self):
        return ""


class LinkDatum(Datum):
    template_name = "museum_site/datum/link-datum.html"

    def __init__(self, *args, **kwargs):
        if "url" not in kwargs:
            raise Exception("Link Datum requires a URL parameter")
        super().__init__(kwargs)


class MultiLinkDatum(Datum):
    template_name = "museum_site/datum/multi-link-datum.html"

    def __init__(self, *args, **kwargs):
        super().__init__(kwargs)


class SSVLinksDatum(Datum):
    template_name = "museum_site/datum/ssv-links-datum.html"

    def __init__(self, *args, **kwargs):
        if not kwargs.get("plural"):
            kwargs["plural"] = "s"
        super().__init__(kwargs)


class LanguageLinksDatum(SSVLinksDatum):
    template_name = "museum_site/datum/language-links-datum.html"
