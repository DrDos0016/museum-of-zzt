from django import forms
from museum_site.constants import TERMS, UPLOAD_CAP


class UploadFileWidget(forms.FileInput):
    template_name = "museum_site/widgets/upload-file-widget.html"
    zfi = []
    filename = ""
    size = 0

    def __init__(self, attrs=None, target_text="TARGET TEXT", allowed_filetypes="", show_size_limit=False):
        super().__init__(attrs)
        self.target_text = target_text
        self.allowed_filetypes = allowed_filetypes
        self.max_upload_size = UPLOAD_CAP
        self.show_size_limit = show_size_limit

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["zfi"] = self.zfi
        context["filename"] = self.filename
        context["size"] = self.size
        context["target_text"] = self.target_text
        context["allowed_filetypes"] = self.allowed_filetypes
        context["max_upload_size"] = self.max_upload_size
        context["show_size_limit"] = self.show_size_limit
        return context

    def set_info(self, filename, file_list, size):
        self.filename = filename
        self.zfi = file_list
        self.size = size


class GroupedCheckboxWidget(forms.MultiWidget):
    template_name = "museum_site/widgets/grouped-checkbox-widget.html",

    def __init__(self, name="", value=[], attrs={}, widgets=[]):
        self.name = name
        self.value = value
        self.attrs = attrs
        self.widgets = widgets

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
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


class Scrolling_Radio_Widget(forms.Select):
    template_name = "museum_site/widgets/scrolling-checklist-widget.html"

    def __init__(self, attrs=None, choices=(), filterable=True, categories=False, buttons=[], show_selected=False, default=[]):
        super().__init__(attrs)
        self.input_method = "radio"
        self.choices = choices
        self.categories = categories
        self.filterable = filterable
        self.buttons = buttons
        self.show_selected = show_selected
        self.default = default

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["name"] = name
        context["choices"] = self.choices
        context["input_method"] = self.input_method
        context["categories"] = self.categories
        context["filterable"] = self.filterable
        context["buttons"] = self.buttons
        context["show_selected"] = self.show_selected
        context["default"] = self.default
        return context


class Ordered_Scrolling_Radio_Widget(forms.SelectMultiple):
    template_name = "museum_site/widgets/ordered-scrolling-list-widget.html"

    def __init__(self, attrs=None, choices=(), filterable=True, categories=False, buttons=[], show_selected=False, default=[]):
        super().__init__(attrs)
        self.input_method = "radio"
        self.choices = choices
        self.categories = categories
        self.filterable = filterable
        self.buttons = buttons
        self.show_selected = show_selected
        self.default = default

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["name"] = name
        context["choices"] = self.choices
        context["input_method"] = self.input_method
        context["categories"] = self.categories
        context["filterable"] = self.filterable
        context["buttons"] = self.buttons
        context["show_selected"] = self.show_selected
        context["default"] = self.default
        return context


class Scrolling_Checklist_Widget(forms.SelectMultiple):
    template_name = "museum_site/widgets/scrolling-checklist-widget.html"

    def __init__(self, attrs=None, choices=(), filterable=True, categories=None, buttons=[], show_selected=False, default=[], input_method="checkbox"):
        super().__init__(attrs)
        self.input_method = input_method
        self.choices = choices
        self.categories = categories
        self.filterable = filterable
        self.buttons = buttons
        self.show_selected = show_selected
        self.default = default

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["name"] = name
        context["choices"] = self.choices
        context["input_method"] = self.input_method
        context["categories"] = self.categories
        context["filterable"] = self.filterable
        context["buttons"] = self.buttons
        context["show_selected"] = self.show_selected
        context["default"] = self.default
        return context


class Language_Checklist_Widget(Scrolling_Checklist_Widget):
    template_name = "museum_site/widgets/language-checklist-widget.html"


class Enhanced_Text_Widget(forms.TextInput):
    template_name = "museum_site/widgets/enhanced-text-widget.html"

    def __init__(self, attrs=None, char_limit=None, prefix_text=""):
        super().__init__(attrs)
        self.char_limit = char_limit
        self.prefix_text = prefix_text

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.char_limit:
            context["char_limit"] = self.char_limit
            context["field_maxlength"] = self.char_limit * 3
        context["prefix_text"] = self.prefix_text
        return context


class Enhanced_Text_Area_Widget(Enhanced_Text_Widget):
    template_name = "museum_site/widgets/enhanced-textarea-widget.html"


class Enhanced_Date_Widget(forms.TextInput):
    template_name = "museum_site/widgets/enhanced-date-widget.html"

    def __init__(self, attrs=None, buttons=[], clear_label="Clear"):
        super().__init__(attrs)
        self.clear_label = clear_label
        if buttons is not None:
            self.buttons = buttons

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["buttons"] = self.buttons
        context["clear_label"] = self.clear_label
        return context


class Associated_Content_Widget(forms.Widget):
    template_name = "museum_site/widgets/associated-content-widget.html"

    def __init__(self, attrs=None, kind=None):
        super().__init__(attrs)

    def value_from_datadict(self, data, files, name):
        return (data.get("reviews"), data.get("articles"))

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value:
            context["reviews"] = value[0]
            context["articles"] = value[1]
        return context


class Tagged_Text_Widget(forms.Widget):
    template_name = "museum_site/widgets/tagged-text-widget.html"

    def __init__(self, attrs=None, suggestions=None, suggestion_key=None):
        super().__init__(attrs)
        self.suggestions = suggestions
        self.suggestion_key = suggestion_key

    def value_from_datadict(self, data, files, name):
        data_list = data.getlist(name)

        if len(data_list) >= 1:
            return ",".join(data_list) + ","
        else:
            return ""

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        if self.suggestions:
            context["suggestions"] = self.suggestions
        if hasattr(self, "manual_data"):
            context["manual_data"] = self.manual_data
        if self.suggestion_key:
            context["suggestion_key"] = self.suggestion_key
        return context


class Range_Widget(forms.Widget):
    template_name = "museum_site/widgets/range-widget.html"

    def __init__(self, attrs=None, min_val=None, max_val=None, max_length=None, step=1, include_clear=False):
        super().__init__(attrs)
        self.min_val = min_val
        self.max_val = max_val
        self.max_length = max_length
        self.step = step
        self.include_clear = include_clear

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["min_val"] = self.min_val
        context["max_val"] = self.max_val
        context["max_length"] = self.max_length
        context["step"] = self.step
        context["include_clear"] = self.include_clear
        if hasattr(self, "manual_data"):
            context["manual_data"] = self.manual_data
        return context


class NEW_Range_Widget(forms.Widget):
    template_name = "museum_site/widgets/NEW-range-widget.html"

    def __init__(self, attrs=None, min_allowed=None, max_allowed=None, max_length=None, step=1, include_clear=False):
        super().__init__(attrs)
        self.min_allowed = min_allowed
        self.max_allowed = max_allowed
        self.max_length = max_length
        self.step = step
        self.include_clear = include_clear

    def value_from_datadict(self, data, files, name):
        return (data.get("rating_min"), data.get("rating_max"))

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["min_allowed"] = self.min_allowed
        context["max_allowed"] = self.max_allowed
        context["max_length"] = self.max_length
        context["step"] = self.step
        context["include_clear"] = self.include_clear
        if value:
            context["min_value"] = value[0]
            context["max_value"] = value[1]
        else:
            context["min_value"] = ""
            context["max_value"] = ""
        return context


class NEW_Board_Range_Widget(forms.Widget):
    template_name = "museum_site/widgets/NEW-board-range-widget.html"

    def __init__(self, attrs=None, min_allowed=None, max_allowed=None, max_length=None, step=1, include_clear=False):
        super().__init__(attrs)
        self.min_allowed = min_allowed
        self.max_allowed = max_allowed
        self.max_length = max_length
        self.step = step
        self.include_clear = include_clear

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["value_class"] = "debug"
        context["min_allowed"] = self.min_allowed
        context["max_allowed"] = self.max_allowed
        context["max_length"] = self.max_length
        context["step"] = self.step
        context["include_clear"] = self.include_clear
        if value:
            context["min_value"] = value[0]
            context["max_value"] = value[1]
            context["board_type"] = value[2]
        else:
            context["min_value"] = ""
            context["max_value"] = ""
            context["board_type"] = ""
        return context

    def value_from_datadict(self, data, files, name):
        return (data.get("board_min"), data.get("board_max"), data.get("board_type"))


class Board_Range_Widget(Range_Widget):
    template_name = "museum_site/widgets/board-range-widget.html"


class Ascii_Character_Widget(forms.TextInput):
    template_name = "museum_site/widgets/ascii-character-widget.html"

    def __init__(self, attrs=None, scale=2, orientation="horiz"):
        super().__init__(attrs)
        self.scale = scale
        self.orientation = orientation

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["range"] = range(0, 256)
        context["scale"] = self.scale
        context["orientation"] = self.orientation
        return context


class Ascii_Color_Widget(forms.Select):
    template_name = "museum_site/widgets/ascii-color-widget.html"

    def __init__(self, choices, attrs=None, allow_transparent=False):
        super().__init__(attrs, choices)
        self.allow_transparent = allow_transparent

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["choices"] = self.choices
        if self.allow_transparent:
            context["choices"].append(("transparent", "Transparent"))
        return context


class Faux_Widget(forms.Widget):
    template_name = ""

    def __init__(self, template_name, attrs=None):
        super().__init__(attrs)
        self.template_name = template_name


class Terms_Of_Service_Widget(forms.CheckboxInput):
    template_name = "museum_site/widgets/terms-of-service-widget.html"

    def __init__(self, attrs=None):
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["terms"] = TERMS
        return context


class Collection_Title_Widget(Enhanced_Text_Widget):
    template_name = "museum_site/widgets/collection-title-widget.html"


class Collection_Arrange_Widget(Scrolling_Checklist_Widget):
    template_name = "museum_site/widgets/collection-arrange-widget.html"
