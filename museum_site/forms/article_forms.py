from django import forms
from django.urls import reverse_lazy

from museum_site.constants import YEAR
from museum_site.fields import Enhanced_Model_Choice_Field
from museum_site.models import Article, Series

class Article_Search_Form(forms.Form):
    use_required_attribute = False
    required = False
    heading = "Article Search"
    attrs = {
        "method": "GET",
        "action": reverse_lazy("article_directory"),
    }
    submit_value = "Search Articles"

    YEARS = (
        [("Any", "- ANY - ")] +
        [(y, y) for y in range(YEAR, 1990, -1)] +
        [("Unk", "Unknown")]
    )

    SORTS = (
        ("title", "Title"),
        ("author", "Author"),
        ("category", "Category"),
        ("-date", "Newest"),
        ("date", "Oldest"),
    )

    title = forms.CharField(label="Title contains", required=False)
    author = forms.CharField(label="Author contains", required=False)
    text = forms.CharField(label="Text contains", required=False)
    year = forms.ChoiceField(label="Publication year", choices=YEARS)
    category = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=Article.CATEGORY_CHOICES)
    series = Enhanced_Model_Choice_Field(label="In Series", queryset=Series.objects.visible(), empty_label="- ANY -")
    sort = forms.ChoiceField(choices=SORTS)
