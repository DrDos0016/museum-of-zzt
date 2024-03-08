from django import forms
from django.urls import reverse

from museum_site.core.detail_identifiers import *
from museum_site.core.sorters import ZFile_Sorter
from museum_site.core.transforms import language_select_choices, range_select_choices
from museum_site.constants import LANGUAGES, YEAR, FORM_ANY, FORM_NONE
from museum_site.fields import Manual_Field, Museum_Related_Content_Field, Museum_Model_Scrolling_Multiple_Choice_Field, Museum_Rating_Field, Museum_Board_Count_Field, Museum_Select_Field, Museum_Choice_Field
from museum_site.models import Detail, Genre
from museum_site.widgets import Associated_Content_Widget, Board_Range_Widget, Range_Widget, Scrolling_Checklist_Widget

class Advanced_Search_Form(forms.Form):
    use_required_attribute = False
    heading = "Advanced Search"
    attrs = {"method": "GET"}
    submit_value = "Search Files"

    title = forms.CharField(label="Title contains", required=False)
    author = forms.CharField(label="Author contains", required=False)
    filename = forms.CharField(label="Filename contains", help_text="Enter a filename used for a zip file", required=False)
    contents = forms.CharField(label="Zip file contents contains", help_text="Enter a filename to find within a zip file", required=False)
    company = forms.CharField(label="Company contains", required=False)
    genre = forms.ModelChoiceField(required=False, queryset=Genre.objects.advanced_search_query(), to_field_name="title", empty_label=FORM_ANY)
    board = Museum_Board_Count_Field(required=False, label="Minimum / Maximum Board Count")
    year = forms.ChoiceField(
        label="Release year",
        choices=range_select_choices(1991, YEAR, allow_any=True, allow_unknown=True, order="desc"),
        required=False,
    )
    rating = Museum_Rating_Field(required=False)
    lang = forms.ChoiceField(
        label="Language",
        choices=language_select_choices(LANGUAGES, allow_any=True, allow_non_english=True),
        required=False,
    )
    associated = Museum_Related_Content_Field(label="Related content", required=False)
    details = Museum_Model_Scrolling_Multiple_Choice_Field(
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
    sort = Museum_Select_Field(
        label="Sort results by",
        choices=ZFile_Sorter().get_sort_options_as_django_choices(),
        full_choices=ZFile_Sorter().get_sort_options_as_django_choices(include_all=True),
        required=False,
    )

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


class View_Explicit_Content_Confirmation_Form(forms.Form):
    use_required_attribute = False
    heading = "Explicit Content Ahead!"
    attrs = {"method": "POST"}
    submit_value = "Continue"

    explicit_warning = Museum_Choice_Field(
        label="Skip this warning",
        widget=forms.RadioSelect(),
        choices=(
            ("on", "Continue to warn about explicit content"),
            ("off", "Do not warn me about explicit content")
        ),
        help_text=(
            "Choose whether or not to be warned about explicit content in the future."
            "If these warnings are disabled, you may re-enable them from <a href='{}'>your profile</a> page."
        ),
        initial="on",
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        self.fields["explicit_warning"].help_text = self.fields["explicit_warning"].help_text.format(reverse("my_profile"))

    def process(self, request):
        if request.POST.get("explicit_warning") == "off":
            request.session["bypass_explicit_content_warnings"] = True
        else:
            if request.session.get("bypass_explicit_content_warnings"):
                del request.session["bypass_explicit_content_warnings"]
