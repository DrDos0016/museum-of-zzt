from datetime import datetime, timezone

from django import forms
from django.urls import reverse_lazy

from museum_site.core.discord import discord_announce_review
from museum_site.core.feedback_tag_identifiers import *
from museum_site.core.form_utils import any_plus, get_sort_option_form_choices
from museum_site.core.sorters import Feedback_Sorter
from museum_site.constants import YEAR
from museum_site.fields import Museum_Model_Multiple_Choice_Field, Museum_Choice_Field, Museum_Select_Field
from museum_site.models import Review, Feedback_Tag
from museum_site.models import File as ZFile
from museum_site.settings import REMOTE_ADDR_HEADER
from museum_site.widgets import Scrolling_Checklist_Widget


class Review_Form(forms.ModelForm):
    attrs = {"method": "POST"}
    mode = "Create"
    RATINGS = (
        (-1, "No rating"), (0, "0.0"), (0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5"), (2.0, "2.0"),
        (2.5, "2.5"), (3.0, "3.0"), (3.5, "3.5"), (4.0, "4.0"), (4.5, "4.5"), (5.0, "5.0"),
    )

    use_required_attribute = False
    rating = forms.ChoiceField(choices=RATINGS, help_text="Optionally provide a numeric score from 0.0 to 5.0",)
    tags = Museum_Model_Multiple_Choice_Field(
        queryset=Feedback_Tag.objects.all(), widget=forms.CheckboxSelectMultiple,
        help_text="If any box is checked, feedback must be tagged with at least one checked tag", required=False
    )
    spotlight = Museum_Choice_Field(
        widget=forms.RadioSelect(),
        choices=(
            (1, "Yes. Showcase this feedback."),
            (0, "No. Do not showcase this feedback.")
        ),
        help_text="Choose whether or not this feedback should be announced on the Museum of ZZT Discord server and appear on the front page.",
        initial=1
    )
    submit_value = "Submit Feedback"

    class Meta:
        model = Review
        fields = ["author", "title", "content", "rating"]
        labels = {"title": "Title", "author": "Your Name", "content": "Feedback"}

        help_texts = {
            "content": (
                '<a href="http://daringfireball.net/projects/markdown/syntax" target="_blank" tabindex="-1">Markdown syntax</a> is supported for '
                'formatting.<br>Additionally, you may place text behind a spoiler tag by wrapping it in two pipe characters '
                '(ex: <span class="mono">||this is hidden||</span>).'
            ),
        }

        widgets = {
            "content": forms.Textarea(attrs={"class":"height-256"})
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

    def process(self, request, zfile, feedback=None):
        if self.mode == "Create":
            feedback = self.save(commit=False)
        else:  # Pull new fields when editing. Others handled later
            feedback.title = self.cleaned_data.get("title")
            feedback.content = self.cleaned_data.get("content")
            feedback.rating = self.cleaned_data.get("rating")

        # Prepare feedback object
        if request.user.is_authenticated:  # Set user and spotlight for logged in users
            feedback.author = request.user.username
            feedback.user_id = request.user.id
            feedback.spotlight = self.cleaned_data.get("spotlight", True)
        else:  # Force spotlight for guests
            feedback.spotlight = True
        feedback.ip = request.META.get(REMOTE_ADDR_HEADER)
        feedback.date = datetime.now(tz=timezone.utc)
        feedback.zfile_id = zfile.pk

        # Simple spam protection
        if zfile.can_review == ZFile.FEEDBACK_APPROVAL or (feedback.content.find("href") != -1) or (feedback.content.find("[url=") != -1):
            feedback.approved = False
        if (not request.user.is_authenticated) and feedback.content.find("http") != -1:
            feedback.approved = False
        if (not request.user.is_authenticated): # TODO Make this a proper constant or setting
            feedback.approved = False

        feedback.save()

        if self.mode == "Edit":
            feedback.tags.clear()

        # Add tags
        for tag in self.cleaned_data["tags"]:
            feedback.tags.add(tag.pk)
        # Force "Review" tag if there's a rating
        if float(self.cleaned_data["rating"]) >= 0:
            feedback.tags.add(FEEDBACK_TAG_REVIEW)

        # Update file's review count/scores if the review is approved
        if feedback.approved and zfile.can_review == ZFile.FEEDBACK_YES:
            zfile.calculate_reviews()
            zfile.calculate_feedback()
            # Make Announcement
            if (not request.user.is_authenticated) or self.cleaned_data.get("spotlight") == "1":  # Guests always have feedback announced
                discord_announce_review(feedback)
            zfile.save()

        return feedback

class Feedback_Edit_Form(Review_Form):
    mode = "Edit"
    zfile_id = forms.IntegerField(widget=forms.HiddenInput)



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
    tags = Museum_Model_Multiple_Choice_Field(
        queryset=Feedback_Tag.objects.all(), widget=forms.CheckboxSelectMultiple,
        help_text="If any box is checked, feedback must be tagged with at least one checked tag", required=False
    )
    review_date = forms.ChoiceField(label="Year of feedback", choices=any_plus(((str(x), str(x)) for x in range(YEAR, (FIRST_FEEDBACK_YEAR - 1), -1))))
    min_rating = forms.ChoiceField(label="Minimum rating", choices=RATINGS)
    max_rating = forms.ChoiceField(label="Maximum rating", choices=RATINGS, initial=5.0)
    ratingless = Museum_Choice_Field(
        layout="horizontal",
        widget=forms.RadioSelect(),
        choices=(
            (1, "Yes"),
            (0, "No")
        ),
        label="Include feedback without a rating", initial=1, required=False
    )
    sort = Museum_Select_Field(
        label="Sort results by",
        choices=Feedback_Sorter().get_sort_options_as_django_choices(),
        full_choices=Feedback_Sorter().get_sort_options_as_django_choices(include_all=True),
        required=False,
    )


class Feedback_Delete_Confirmation_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Delete This Feedback"
    attrs = {"method": "POST"}

    confirmation = forms.CharField(
        max_length=6,
        help_text="To confirm you have the correct feedback and wish to delete it please type \"DELETE\" in the following text field.",
    )
    zfile_key = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["confirmation"].widget.attrs["placeholder"] = "DELETE"

    def clean_confirmation(self):
        if self.cleaned_data["confirmation"].upper() != "DELETE":
            self.add_error("confirmation", "You must provide confirmation before an upload can be deleted!")
