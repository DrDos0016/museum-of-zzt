from django import forms
from django.core.exceptions import ValidationError

from museum_site.constants import LANGUAGES, YEAR, FORM_ANY, FORM_NONE, TERMS
from museum_site.core.detail_identifiers import *
from museum_site.core.transforms import language_select_choices, range_select_choices
from museum_site.fields import *
from museum_site.models import Article, Detail, Genre, Series, Review, Feedback_Tag
from museum_site.widgets import *

STUB_CHOICES = (("A", "First"), ("B", "Second"), ("C", "Third"))


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

    COLOR_CHOICES = (
        ("black", "Black"),
        ("blue", "Blue"),
        ("green", "Green"),
        ("cyan", "Cyan"),
        ("red", "Red"),
        ("purple", "Purple"),
        ("yellow", "Yellow"),
        ("white", "White"),
        ("darkgray", "Dark Gray"),
        ("darkblue", "Dark Blue"),
        ("darkgreen", "Dark Green"),
        ("darkcyan", "Dark Cyan"),
        ("darkred", "Dark Red"),
        ("darkpurple", "Dark Purple"),
        ("darkyellow", "Dark Yellow"),
        ("gray", "Gray")
    )

    title = forms.CharField(widget=Enhanced_Text_Widget(char_limit=80))
    hosted_on = forms.CharField(widget=Enhanced_Text_Widget(prefix_text="Hosted on..."))
    field_a = forms.CharField(help_text="Barebones Text Entry")
    field_b = forms.CharField(label="Filename contains", help_text="Enter a filename used for a zip file", required=False)
    author = Museum_Tagged_Text_Field(
        required=False,
        help_text=(
            "Separate multiple authors with a comma. Do not abbreviate "
            "names.<br>"
            "For files with many authors, consider using the compiler as "
            "the author with \"Various\" to represent the rest. Try to "
            "sort multiple authors from most to least important on this "
            "particular upload. If the author's name is not known, leave this "
            "field blank."
        ),
    )
    genre = forms.ModelChoiceField(required=False, queryset=Genre.objects.advanced_search_query(), to_field_name="title", empty_label=FORM_ANY)
    rating = Museum_Rating_Field(required=False)
    board = Museum_Board_Count_Field(required=False, label="Minimum / Maximum Board Count")
    year = forms.ChoiceField(
        label="Release year",
        choices=range_select_choices(1991, YEAR, allow_any=True, allow_unknown=True, order="desc"),
        required=False,
    )
    release_date = forms.CharField(widget=Enhanced_Date_Widget(buttons=["today", "clear"], clear_label="Unknown"))
    lang = forms.ChoiceField(
        label="Language",
        choices=language_select_choices(LANGUAGES, allow_any=True, allow_non_english=True),
        required=False,
    )
    associated = Museum_Related_Content_Field(label="Related content", required=False)
    genre = Museum_Model_Scrolling_Multiple_Choice_Field(
        widget=Scrolling_Checklist_Widget(buttons=["Clear"], show_selected=True),
        queryset=Genre.objects.visible(),
        required=False,
        help_text=(
            "Check any applicable genres that describe the content of the uploaded file. Use 'Other' if a genre isn't represented and mention it in the upload"
            "notes field in the Upload Settings section. For a description of genres, see the <a href='/help/genre/' target='_blank'>Genre Overview</a> page."
        )
    )
    details = Museum_Model_Scrolling_Multiple_Choice_Field(
        required=False,
        queryset=Detail.objects.visible(),
        initial=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED, DETAIL_WEAVE],
        to_field_name="pk",
        widget=Scrolling_Checklist_Widget(
            categories=["ZZT", "SZZT", "Media", "Other"],
            default=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED, DETAIL_WEAVE],
            buttons=["Clear", "Default"],
            show_selected=True,
        )
    )
    category = Museum_Multiple_Choice_Field(required=False, widget=forms.CheckboxSelectMultiple, choices=Article.CATEGORY_CHOICES, layout="multi-column")
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
    tags = Museum_Model_Multiple_Choice_Field(
        queryset=Feedback_Tag.objects.all(), widget=forms.CheckboxSelectMultiple,
        help_text="If any box is checked, feedback must be tagged with at least one checked tag", required=False
    )
    ratingless = Museum_Choice_Field(
        layout="horizontal",
        widget=forms.RadioSelect(),
        choices=(
            (1, "Yes"),
            (0, "No")
        ),
        label="Include feedback without a rating", initial=1, required=False
    )

    character = forms.IntegerField(
        min_value=0,
        max_value=255,
        widget=Ascii_Character_Widget(),
        help_text="Click on an ASCII character in the table to select it",
    )
    foreground = Museum_Color_Choice_Field(choices=COLOR_CHOICES, widget=Ascii_Color_Widget(choices=COLOR_CHOICES))
    background = Museum_Color_Choice_Field(choices=COLOR_CHOICES, widget=Ascii_Color_Widget(choices=COLOR_CHOICES, allow_transparent=True))
    text_entry = forms.CharField(widget=forms.Textarea)
    text_entry_tall = forms.CharField(widget=forms.Textarea(attrs={"class": "height-256"}))
    sort = forms.ChoiceField(choices=SORTS)
    terms = Museum_TOS_Field()
