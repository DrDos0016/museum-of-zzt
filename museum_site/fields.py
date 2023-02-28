from django import forms
from museum_site.widgets import *


class IntegerRangeField(forms.MultiValueField):
    def ___init__(self, **kwargs):
        fields = (
            IntegerField(),
            IntegerField(),
        )

        super().__init__(fields=fields, require_all_fields=False, **kwargs)

    def compress(self, data):
        return "-".join(data)


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
