from django import forms
from django.urls import reverse_lazy

from museum_site.constants import YEAR, FORM_ANY, FORM_NONE
from museum_site.core.sorters import Article_Sorter
from museum_site.fields import Enhanced_Model_Choice_Field, Museum_Multiple_Choice_Field, Museum_Select_Field
from museum_site.models import Article, Series

class Zeta_Configuration_Form(forms.Form):
    use_required_attribute = False
    required = False
    submit_value = "Apply Configuration"

    EXECUTABLES = (
        ("", "Automatic"),
        ("32compat", "Preferred ZZT v3.2 Compatible"),
        ("zzt", "ZZT v3.2"),
        ("czoo", "ClassicZoo"),
        ("solidhud", "SolidHUD"),
        ("cleenzzt-moz", "CleenZZT"),
        ("szzt", "Super ZZT v2.0"),
        ("included", "Use Included EXE"),
    )

    CHARSETS = (
        ("", "Automatic"),
        ("cp437", "Code Page 437"),
        ("mzx", "MegaZeux"),
    )

    BLINKS = (
        ("", "Automatic (Including Duration)"),
        ("on", "Enabled - Use Specified Duration"),
        ("noblink", "Disabled - Use High-Intensity Backgrounds"),
        ("loblink", "Disabled - Force Low-Intensity Backgrounds"),
    )

    executable = forms.ChoiceField(label="Executable", choices=EXECUTABLES, required=False)
    charset = forms.ChoiceField(label="Charset", choices=CHARSETS, required=False)
    blink = forms.ChoiceField(label="Blinking", choices=BLINKS, required=False)
    blink_duration = forms.FloatField(label="Blink Duration", initial=0.534, help_text="Length of each phase of the blink cycle in seconds. Default is 0.534s.", required=False)
