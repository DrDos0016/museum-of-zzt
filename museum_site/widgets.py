from django import forms


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
