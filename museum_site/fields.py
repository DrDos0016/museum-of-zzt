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
