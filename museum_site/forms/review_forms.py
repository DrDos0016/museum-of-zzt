from django import forms
from django.urls import reverse_lazy

from museum_site.core.form_utils import any_plus, get_sort_option_form_choices
from museum_site.constants import YEAR
from museum_site.models import Review


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

    class Meta:
        model = Review
        fields = ["author", "title", "content", "rating"]
        labels = {"title": "Review Title", "author": "Your Name", "content": "Review"}

        help_texts = {
            "content": (
                '<a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" tabindex="-1">Markdown syntax</a> is supported for formatting.'
            ),
        }

    def clean_author(self):
        # Replace blank authors with "Unknown"
        author = self.cleaned_data["author"]

        if author == "" or author.lower() == "n/a":
            author = "Anonymous"

        if author.find("/") != -1:
            raise forms.ValidationError("Author may not contain slashes.")

        return author


class Review_Search_Form(forms.Form):
    FIRST_REVIEW_YEAR = 2002
    RATINGS = (
        (0, "0.0"), (0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5"), (2.0, "2.0"), (2.5, "2.5"), (3.0, "3.0"), (3.5, "3.5"), (4.0, "4.0"), (4.5, "4.5"), (5.0, "5.0"),
    )

    heading = "Review Search"
    attrs = {"method": "GET", "action": reverse_lazy("review_directory")}
    submit_value = "Search Reviews"

    # Fields
    use_required_attribute = False
    title = forms.CharField(label="Title contains", required=False)
    author = forms.CharField(label="Author contains", required=False)
    text = forms.CharField(label="Text contains", required=False)
    review_date = forms.ChoiceField(label="Year reviewed", choices=any_plus(((str(x), str(x)) for x in range(YEAR, (FIRST_REVIEW_YEAR - 1), -1))))
    min_rating = forms.ChoiceField(label="Minimum rating", choices=RATINGS)
    max_rating = forms.ChoiceField(label="Maximum rating", choices=RATINGS, initial=5.0)
    ratingless = forms.BooleanField(label="Include reviews without ratings", initial=True, required=False)
    sort = forms.ChoiceField(label="Sort results by", choices=get_sort_option_form_choices(Review.sort_options))
