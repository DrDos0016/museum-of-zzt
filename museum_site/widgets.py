from django import forms

from .common import GENRE_LIST


class GenreCheckboxWidget(forms.Widget):
    template_name = "museum_site/widgets/genre-checkbox-widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["genres"] = GENRE_LIST
        return context


class SlashSeparatedValueWidget(forms.Widget):
    template_name = "museum_site/widgets/slash-separated-value-widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        print(context)
        return context


class UploadFileWidget(forms.Widget):
    template_name = "museum_site/widgets/upload-file-widget.html"
