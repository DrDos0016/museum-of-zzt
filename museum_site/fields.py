from django import forms
from .widgets import *


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
        print("TEST", test)
        super().__init__(**kwargs)