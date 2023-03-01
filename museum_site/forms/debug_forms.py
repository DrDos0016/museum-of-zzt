from django import forms

STUB_CHOICES = (("A", "First"), ("B", "Second"), ("C", "Third"))

""" These forms might not currently be implemented on the Museum """

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
    details = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(
            choices=qs_to_categorized_select_choices(
                Detail.objects.visible,
                category_order=["ZZT", "SZZT", "Media", "Other"]
            ),
            categories=True,
            buttons=["Clear", "Default"],
            show_selected=True,
            default=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_WEAVE]
        ),
        choices=qs_to_categorized_select_choices(Detail.objects.visible, category_order=["ZZT", "SZZT", "Media", "Other"]),
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


class Social_Media_Shotgun_Form(forms.Form):
    use_required_attribute = False
    heading = "Social Media Shotgun"
    submit_value = "Post"
    attrs = {"method": "POST"}

    ACCOUNTS = (
        ("twitter", "Twitter"),
        ("tumblr", "Tumblr"),
        ("mastodon", "Mastodon"),
        ("patreon", "Patreon"),
        ("discord", "Discord"),
        ("cohost", "Cohost"),
    )

    KINDS = (
        ("misc", "—"),
        ("stream-live", "Going Live"),
        ("stream-schedule", "Stream Schedule"),
        ("stream-promo", "Stream Promo"),
        ("patreon-plug", "Patreon Plug"),
        ("project-update", "Project Update Post"),
    )

    kinds = forms.ChoiceField(choices=KINDS, label="Post Type")

    body = forms.CharField(
        widget=Enhanced_Text_Area_Widget(char_limit=9999),
        help_text="Tweets are limited to 240 characters.<br>Toots are limited to 500 characters.",
    )

    media = forms.FileField(
        required=False,
        help_text="Select the media you wish to upload.",
        label="Media", widget=UploadFileWidget(target_text="Drag & Drop Media Here or Click to Choose")
    )

    accounts = forms.MultipleChoiceField(
        required=False, widget=forms.CheckboxSelectMultiple, choices=ACCOUNTS,
        initial=["twitter", "tumblr", "mastodon"]
    )
