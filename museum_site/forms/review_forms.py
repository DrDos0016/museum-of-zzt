from django import forms
from django.urls import reverse_lazy

from museum_site.core.form_utils import any_plus, get_sort_option_form_choices
from museum_site.constants import YEAR
from museum_site.models import Review, Feedback_Tag
from museum_site.widgets import Scrolling_Checklist_Widget


class Review_Form(forms.ModelForm):
    RATINGS = (
        (-1, "No rating"), (0, "0.0"), (0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5"), (2.0, "2.0"),
        (2.5, "2.5"), (3.0, "3.0"), (3.5, "3.5"), (4.0, "4.0"), (4.5, "4.5"), (5.0, "5.0"),
    )

    use_required_attribute = False
    rating = forms.ChoiceField(
        choices=RATINGS,
        help_text="Optionally provide a numeric score from 0.0 to 5.0",
    )
    spotlight = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=(
            (1, "Yes. Showcase this feedback."),
            (0, "No. Do not showcase this feedback.")
        ),
        help_text="Choose whether or not this feedback should be announced on the Museum of ZZT Discord server and appear on the front page.",
        initial=1
    )

    class Meta:
        model = Review
        fields = ["author", "title", "content", "rating", "tags"]
        labels = {"title": "Title", "author": "Your Name", "content": "Feedback"}

        help_texts = {
            "content": (
                '<a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" tabindex="-1">Markdown syntax</a> is supported for '
                'formatting.<br>Additionally, you may place text behind a spoiler tag by wrapping it in two pipe characters '
                '(ex: <span class="mono">||this is hidden||</span>).'
            ),
        }

        widgets = {
            "tags": Scrolling_Checklist_Widget(filterable=False, buttons=None, show_selected=False),
        }

    def clean_author(self):
        # Replace blank authors with "Unknown"
        author = self.cleaned_data["author"]

        if author == "" or author.lower() == "n/a":
            author = "Anonymous"

        if author.find("/") != -1:
            raise forms.ValidationError("Author may not contain slashes.")

        return author

    def clean_tags(self):
        tags = self.cleaned_data["tags"]
        rating = float(self.cleaned_data["rating"])

        if rating == -1 and not tags.exists():  # Feedback with rating will force the Review tag later in processing
            raise forms.ValidationError("Feedback must be given at least one tag.")
        return tags


class Review_Search_Form(forms.Form):
    FIRST_FEEDBACK_YEAR = 2002
    RATINGS = (
        (0, "0.0"), (0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5"), (2.0, "2.0"), (2.5, "2.5"), (3.0, "3.0"), (3.5, "3.5"), (4.0, "4.0"), (4.5, "4.5"), (5.0, "5.0"),
    )

    heading = "Feedback Search"
    attrs = {"method": "GET", "action": reverse_lazy("review_browse")}
    submit_value = "Search Reviews"

    # Fields
    use_required_attribute = False
    title = forms.CharField(label="Title contains", required=False)
    author = forms.CharField(label="Author contains", required=False)
    content = forms.CharField(label="Text contains", required=False)
    tags = forms.ModelMultipleChoiceField(
        queryset=Feedback_Tag.objects.all(), widget=Scrolling_Checklist_Widget(filterable=False, buttons=None, show_selected=False),
        help_text="If any box is checked, feedback must be tagged with at least one checked tag", required=False
    )
    review_date = forms.ChoiceField(label="Year of feedback", choices=any_plus(((str(x), str(x)) for x in range(YEAR, (FIRST_FEEDBACK_YEAR - 1), -1))))
    min_rating = forms.ChoiceField(label="Minimum rating", choices=RATINGS)
    max_rating = forms.ChoiceField(label="Maximum rating", choices=RATINGS, initial=5.0)
    ratingless = forms.BooleanField(label="Include feedback without a rating", initial=True, required=False)
    sort = forms.ChoiceField(label="Sort results by", choices=get_sort_option_form_choices(Review.sort_options))
