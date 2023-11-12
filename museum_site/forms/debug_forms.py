from django import forms
from django.core.exceptions import ValidationError

from museum_site.constants import LANGUAGES, YEAR, FORM_ANY, FORM_NONE
from museum_site.core.detail_identifiers import *
from museum_site.core.transforms import language_select_choices, range_select_choices
from museum_site.fields import Enhanced_Model_Choice_Field
from museum_site.models import Article, Detail, Genre, Series, Review, Feedback_Tag
from museum_site.widgets import Associated_Content_Widget, NEW_Board_Range_Widget, NEW_Range_Widget, Scrolling_Checklist_Widget

STUB_CHOICES = (("A", "First"), ("B", "Second"), ("C", "Third"))

""" These forms might not currently be implemented on the Museum """

"""
class Debug_Form(forms.Form):
    use_required_attribute = False
    manual_fields = ["board", "associated", "ssv_author", "rating"]

    file_radio = forms.ChoiceField(
        widget=Scrolling_Radio_Widget(choices=associated_file_choices()),
        choices=associated_file_choices(),
        label="File Select Radio Widget",
        help_text="Selecting one file as radio buttons",
        required=False,
    )
    file_check = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(choices=associated_file_choices()),
        choices=associated_file_choices(),
        label="File Select Checkbox Widget",
        help_text="Selecting many files via checkboxes",
        required=False,
    )
    limited_text = forms.CharField(
        widget=Enhanced_Text_Widget(char_limit=69),
        label="Limited Text Field",
        help_text="You get 69 characters. Nice.",
        required=False,
    )
    date_with_buttons = forms.DateField(
        widget=Enhanced_Date_Widget(buttons=["today", "clear"], clear_label="Unknown"),
        label="Date Field With Buttons",
        help_text="Today and Unknown",
        required=False,
    )
    board = Manual_Field(
        widget=Board_Range_Widget(min_val=0, max_val=999, max_length=3),
        required=False,
    )
    associated = Manual_Field(
        label="Related Content",
        widget=Associated_Content_Widget(),
        required=False,
    )
    nonfilterable = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(
            choices=(("A", "A"), ("B", "B"), ("C", "C")),
            filterable=False,
            buttons=["All", "Clear", "Default"],
            show_selected=True,
            default=["A", "C"]
        ),
        choices=(("A", "A"), ("B", "B"), ("C", "C")),
        required=False,
    )
    ssv_author = Manual_Field(
        label="Author(s)",
        widget=Tagged_Text_Widget(),
        required=False,
    )
    rating = Manual_Field(
        label="Rating range",
        widget=Range_Widget(min_val=0, max_val=5, max_length=4, step=0.1),
        required=False,
    )

    def __init__(self, data=None):
        super().__init__(data)
        # Handle Manual Fields
        for field in self.manual_fields:
            self.fields[field].widget.manual_data = self.data.copy()  # Copy to make mutable
            # Coerce specific min/max inputs to generic min/max keys
            self.fields[field].widget.manual_data["min"] = self.fields[field].widget.manual_data.get(field + "_min")
            self.fields[field].widget.manual_data["max"] = self.fields[field].widget.manual_data.get(field + "_max")
            # Tags need to be joined as a string
            if data and isinstance(self.fields[field].widget, Tagged_Text_Widget):
                raw = self.data.getlist(field)
                joined = ",".join(raw) + ","
                if len(joined) > 1:
                    self.fields[field].widget.manual_data["tags_as_string"] = joined

class Zeta_Advanced_Form(forms.Form):
    use_required_attribute = False
    zeta_config = forms.ChoiceField(choices=(("A", "A"), ("B", "B"), ("C", "C")))
    zeta_disable_params = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=STUB_CHOICES
    )
    executable = forms.ChoiceField(choices=(("A", "A"), ("B", "B"), ("C", "C")))
    blink_duration = forms.IntegerField()
    charset_override = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=STUB_CHOICES
    )
    buffer_size = forms.IntegerField()
    sample_rate = forms.IntegerField()
    note_delay = forms.IntegerField()
    volume = forms.IntegerField()
    included_zfiles = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=STUB_CHOICES
    )
    show_again = forms.BooleanField()
"""

class Museum_Rating_Field(forms.Field):
    widget = NEW_Range_Widget(min_allowed=0, max_allowed=5, max_length=4, step=0.01, include_clear=True)

    def clean(self, val):
        min_val = float(val[0]) if val[0] else None
        max_val = float(val[1]) if val[1] else None

        if (min_val is not None and max_val is not None):
            if min_val > max_val:
                raise ValidationError("Minimum rating must not be larger than maximum rating")
        return (min_val, max_val)


class Museum_Board_Count_Field(forms.Field):
    widget = NEW_Board_Range_Widget(min_allowed=0, max_allowed=None, max_length=4, step=0.01, include_clear=True)
    layout = "field-layout-board-count"

    def clean(self, val):
        min_val, max_val = (None, None)
        print("SUBMITTED VAL", val)
        if val is not None:
            min_val = float(val[0]) if val[0] else None
            max_val = float(val[1]) if val[1] else None


        if (min_val is not None and max_val is not None):
            if min_val > max_val:
                raise ValidationError("Minimum board count must not be larger than maximum board count")
        return (min_val, max_val)


class Museum_Related_Content_Field(forms.Field):
    widget=Associated_Content_Widget()
    layout = "field-layout-flex-wrap"

    def clean(self, val):
        min_val, max_val = (None, None)
        print("SUBMITTED VAL", val)
        if val is not None:
            min_val = float(val[0]) if val[0] else None
            max_val = float(val[1]) if val[1] else None

        if (min_val is not None and max_val is not None):
            if min_val > max_val:
                raise ValidationError("Minimum board count must not be larger than maximum board count")
        return (min_val, max_val)


class Museum_Multiple_Choice_Field(forms.MultipleChoiceField):
    layout = "field-layout-multi-column-list"

class Museum_Choice_Field(forms.ChoiceField):
    layout = "field-layout-list"



class Debug_Form_2023(forms.Form):
    use_required_attribute = False
    attrs = {"method": "POST"}
    submit_value = "Submit Debug Form"
    heading = "Debug Form 2023"

    SORTS = (
        ("title", "Title"),
        ("author", "Author"),
        ("category", "Category"),
        ("-date", "Newest"),
        ("date", "Oldest"),
    )

    field_a = forms.CharField(help_text="Barebones Text Entry")
    field_b = forms.CharField(label="Filename contains", help_text="Enter a filename used for a zip file", required=False)
    genre = forms.ModelChoiceField(required=False, queryset=Genre.objects.advanced_search_query(), to_field_name="title", empty_label=FORM_ANY)
    rating = Museum_Rating_Field(required=False)
    board = Museum_Board_Count_Field(required=False, label="Minimum / Maximum Board Count")
    year = forms.ChoiceField(
        label="Release year",
        choices=range_select_choices(1991, YEAR, allow_any=True, allow_unknown=True, order="desc"),
        required=False,
    )
    lang = forms.ChoiceField(
        label="Language",
        choices=language_select_choices(LANGUAGES, allow_any=True, allow_non_english=True),
        required=False,
    )
    associated = Museum_Related_Content_Field(
        label="Related content",
        required=False,
    )
    details = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Detail.objects.visible(),
        initial=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED, DETAIL_WEAVE],
        to_field_name="pk",
        widget=Scrolling_Checklist_Widget(
            categories = ["ZZT", "SZZT", "Media", "Other"],
            default=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED, DETAIL_WEAVE],
            buttons=["Clear", "Default"],
            show_selected=True,
        )
    )
    category = Museum_Multiple_Choice_Field(required=False, widget=forms.CheckboxSelectMultiple, choices=Article.CATEGORY_CHOICES)
    series = Enhanced_Model_Choice_Field(label="In Series", queryset=Series.objects.visible(), empty_label=FORM_ANY)
    spotlight = Museum_Choice_Field(
        widget=forms.RadioSelect(),
        choices=(
            (1, "Yes. Showcase this feedback."),
            (0, "No. Do not showcase this feedback.")
        ),
        help_text="Choose whether or not this feedback should be announced on the Museum of ZZT Discord server and appear on the front page.",
        initial=1
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Feedback_Tag.objects.all(), widget=Scrolling_Checklist_Widget(filterable=False, buttons=None, show_selected=False),
        help_text="If any box is checked, feedback must be tagged with at least one checked tag", required=False
    )
    ratingless = forms.BooleanField(label="Include feedback without a rating", initial=True, required=False)
    sort = forms.ChoiceField(choices=SORTS)
