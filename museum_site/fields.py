from django import forms
from django.core.exceptions import ValidationError

from museum_site.widgets import *

MUSEUM_FIELD_LAYOUTS = {
    "list": "field-layout-list",
    "horizontal": "field-layout-list field-layout-horizontal",
    "multi-column": "field-layout-list field-layout-multi-column",
}


class GetField(forms.Field):
    def __init__(self, test=None, **kwargs):
        super().__init__(**kwargs)


class Manual_Field(forms.NullBooleanField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Faux_Field(forms.NullBooleanField):
    """ Used for fake fields that don't contain user specified information but should still be worked into the form """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Tag_List_Field(forms.MultipleChoiceField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python(self, value):
        output = []
        if not value:
            return output
        value = value.split(",")
        for item in value:
            output.append(str(item))
        return output

    def validate(self, value):
        pass  # All data entered is valid


class Enhanced_Model_Choice_Field(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.to_select()

    def clean(self, value):
        return value


class Choice_Field_No_Validation(forms.ChoiceField):
    """ Allows a list of choices where any value is treated as valid. Used for specifying preview images on upload. """
    def valid_value(self, value):
        return True


# THE NEW STUFF
class Museum_Board_Count_Field(forms.Field):
    widget = NEW_Board_Range_Widget(min_allowed=0, max_allowed=None, max_length=4, step=0.01, include_clear=True)
    layout = "field-layout-board-count"

    def clean(self, val):
        min_val, max_val = (None, None)
        print("SUBMITTED VAL", val)
        if val is not None:
            if val[2] is None and (val[0] != "" and val[1] != ""):
                raise ValidationError("Filter requires playable or total board count to be specified")
            min_val = float(val[0]) if val[0] else None
            max_val = float(val[1]) if val[1] else None

        if (min_val is not None and max_val is not None):
            if min_val > max_val:
                raise ValidationError("Minimum board count must not be larger than maximum board count")
        return (min_val, max_val)


class Museum_Rating_Field(forms.Field):
    widget = NEW_Range_Widget(min_allowed=0, max_allowed=5, max_length=4, step=0.01, include_clear=True)

    def clean(self, val):
        min_val = float(val[0]) if val[0] else None
        max_val = float(val[1]) if val[1] else None

        if (min_val is not None and max_val is not None):
            if min_val > max_val:
                raise ValidationError("Minimum rating must not be larger than maximum rating")
        return (min_val, max_val)


class Museum_Related_Content_Field(forms.Field):
    layout = "field-layout-list field-layout-horizontal field-layout-related-content"
    widget = Associated_Content_Widget


class Museum_Choice_Field(forms.ChoiceField):
    layout = "field-layout-list"
    layouts = MUSEUM_FIELD_LAYOUTS

    def __init__(self, *args, **kwargs):
        if kwargs.get("layout") and self.layouts.get(kwargs["layout"]):
            self.layout = self.layouts.get(kwargs["layout"])
            del kwargs["layout"]
        super().__init__(*args, **kwargs)


class Museum_Multiple_Choice_Field(forms.MultipleChoiceField):
    layout = "field-layout-list"
    layouts = MUSEUM_FIELD_LAYOUTS

    def __init__(self, *args, **kwargs):
        if kwargs.get("layout") and self.layouts.get(kwargs["layout"]):
            self.layout = self.layouts.get(kwargs["layout"])
            del kwargs["layout"]
        super().__init__(*args, **kwargs)


class Museum_Model_Choice_Field(forms.ModelChoiceField):
    layout = "field-layout-list"
    layouts = MUSEUM_FIELD_LAYOUTS

    def __init__(self, *args, **kwargs):
        if kwargs.get("layout") and self.layouts.get(kwargs["layout"]):
            self.layout = self.layouts.get(kwargs["layout"])
            del kwargs["layout"]
        super().__init__(*args, **kwargs)


class Museum_Model_Multiple_Choice_Field(forms.ModelMultipleChoiceField):
    layout = "field-layout-list"


class Museum_Scrolling_Multiple_Choice_Field(forms.MultipleChoiceField):
    layout = "field-layout-scrolling-list"


class Museum_Model_Scrolling_Multiple_Choice_Field(forms.ModelMultipleChoiceField):
    layout = "field-layout-scrolling-list"


class Museum_Color_Choice_Field(forms.ChoiceField):
    layout = "field-layout-color"


class Museum_Tagged_Text_Field(forms.CharField):
    layout = "field-layout-tagged-text"
    widget = Tagged_Text_Widget

class Museum_TOS_Field(forms.BooleanField):
    layout = "field-layout-tos"
    widget = Terms_Of_Service_Widget


class Museum_Drag_And_Drop_File_Field(forms.FileField):
    layout = "field-layout-file-uploader"
    widget = UploadFileWidget()
