from django import forms


class SelectPlusAnyWidget(forms.Select):
    template_name = "museum_site/widgets/select-plus-any-widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["choices"] = self.choices
        return context


class SelectPlusCustomWidget(forms.Select):
    template_name = "museum_site/widgets/select-plus-custom-widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["choices"] = self.choices
        return context


class SlashSeparatedValueCheckboxWidget(forms.Select):
    template_name = (
        "museum_site/widgets/slash-separated-value-checkbox-widget.html"
    )

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["name"] = name
        context["choices"] = self.choices
        context["value"] = value
        return context


class SlashSeparatedValueWidget(forms.Widget):
    template_name = "museum_site/widgets/slash-separated-value-widget.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["value"] = value
        return context


class UploadFileWidget(forms.FileInput):
    template_name = "museum_site/widgets/upload-file-widget.html"
    zfi = []
    filename = ""
    size = 0

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["zfi"] = self.zfi
        context["filename"] = self.filename
        context["size"] = self.size
        return context


    def set_info(self, filename, file_list, size):
        self.filename = filename
        self.zfi = file_list
        self.size = size


class GroupedCheckboxWidget(forms.MultiWidget):
    template_name = "museum_site/widgets/grouped-checkbox-widget.html",

    def __init__(self, name="", value=[], attrs={}, widgets=[]):
        #super().__init__(widgets=widgets)
        self.name = name
        self.value = value
        self.attrs = attrs
        self.widgets = widgets

        pass

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        #context["choices"] = self.choices
        context["choices"] = self.add_headers(self.choices)
        context["name"] = name
        context["value"] = value
        return context


    def add_headers(self, choices):
        output = []
        for c in choices:
            header = "Other"
            if c[1].startswith("ZZT "):
                header = "ZZT"
            elif c[1].startswith("Super ZZT "):
                header = "Super ZZT"
            elif c[1] in [
                "Image", "Video", "Audio", "Text", "ZZM Audio", "HTML Document"
            ]:
                header = "Media"
            output.append((c[0], c[1], header))
        return output
