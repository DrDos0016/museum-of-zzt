from django import forms

from museum_site.core.detail_identifiers import *
from museum_site.core.transforms import language_select_choices, range_select_choices
from museum_site.constants import LANGUAGES, YEAR, FORM_ANY, FORM_NONE
from museum_site.fields import Manual_Field
from museum_site.models import Detail, Genre
from museum_site.widgets import Associated_Content_Widget, Board_Range_Widget, Range_Widget, Scrolling_Checklist_Widget

class Advanced_Search_Form(forms.Form):
    use_required_attribute = False
    heading = "Advanced Search"
    attrs = {"method": "GET"}
    submit_value = "Search Files"
    manual_fields = ["board", "rating", "associated"]

    title = forms.CharField(label="Title contains", required=False)
    author = forms.CharField(label="Author contains", required=False)
    filename = forms.CharField(label="Filename contains", required=False)
    contents = forms.CharField(label="Zip file contents contains", help_text="Enter a filename to search for in the file's zip file", required=False)
    company = forms.CharField(label="Company contains", required=False)
    genre = forms.ModelChoiceField(required=False, queryset=Genre.objects.advanced_search_query(), to_field_name="title", empty_label=FORM_ANY)
    board = Manual_Field(
        label="Minimum / Maximum board count",
        widget=Board_Range_Widget(min_val=0, max_val=999, max_length=3),
        required=False,
    )
    year = forms.ChoiceField(
        label="Release year",
        choices=range_select_choices(1991, YEAR, allow_any=True, allow_unknown=True, order="desc"),
        required=False,
    )
    rating = Manual_Field(
        label="Minimum / Maximum rating",
        widget=Range_Widget(min_val=0, max_val=5, max_length=4, step=0.1, include_clear=True),
        required=False,
        help_text="User input must be a number ranging from 0.0 to 5.0"
    )
    lang = forms.ChoiceField(
        label="Language",
        choices=language_select_choices(LANGUAGES, allow_any=True, allow_non_english=True),
        required=False,
    )
    associated = Manual_Field(
        label="Related content",
        widget=Associated_Content_Widget(),
        required=False,
    )
    details = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Detail.objects.visible(),
        to_field_name="pk",
        widget=Scrolling_Checklist_Widget(
            categories = ["ZZT", "SZZT", "Media", "Other"],
            default=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED, DETAIL_WEAVE],
            buttons=["Clear", "Default"],
            show_selected=True,
        )
    )
    sort = forms.ChoiceField(
        label="Sort results by",
        choices=(
            ("title", "Title"),
            ("author", "Author"),
            ("company", "Company"),
            ("rating", "Rating"),
            ("release", "Release Date"),
        ),
        required=False,
    )

    def __init__(self, data=None, initial={}):
        super().__init__(data, initial=initial)
        for field in self.manual_fields:
            self.fields[field].widget.manual_data = self.data.copy()  # Copy to make mutable
            # Coerce specific min/max inputs to generic min/max keys
            self.fields[field].widget.manual_data["min"] = self.fields[field].widget.manual_data.get(field + "_min")
            self.fields[field].widget.manual_data["max"] = self.fields[field].widget.manual_data.get(field + "_max")

    def clean_board(self):
        return self.clean_range("board", 0, 999, "Minimum board count is larger than maximum board count")

    def clean_rating(self):
        return self.clean_range("rating", 0, 5, "Minimum rating is larger than maximum rating")

    def clean_range(self, field_name, allowed_min, allowed_max, error_message):
        requested_min = self.data.get(field_name + "_min", allowed_min)
        requested_max = self.data.get(field_name + "_max", allowed_max)

        if requested_min != "" or requested_max != "":
            if requested_min == "":
                requested_min = allowed_min
            if requested_max == "":
                requested_max = allowed_max
            requested_min = float(requested_min)
            requested_max = float(requested_max)

            if requested_max < requested_min:
                self.add_error(field_name, error_message)

        return []
