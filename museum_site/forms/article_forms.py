from django import forms
from django.urls import reverse_lazy

from museum_site.constants import YEAR, FORM_ANY, FORM_NONE
from museum_site.core.sorters import Article_Sorter
from museum_site.fields import Enhanced_Model_Choice_Field, Museum_Multiple_Choice_Field, Museum_Select_Field
from museum_site.models import Article, Series

class Article_Search_Form(forms.Form):
    use_required_attribute = False
    required = False
    heading = "Article Search"
    attrs = {
        "method": "GET",
        "action": reverse_lazy("article_search"),
    }
    submit_value = "Search Articles"

    YEARS = (
        [("Any", FORM_ANY)] +
        [(y, y) for y in range(YEAR, 1990, -1)] +
        [("Unk", "Unknown")]
    )

    title = forms.CharField(label="Title contains", required=False)
    author = forms.CharField(label="Author contains", required=False)
    text = forms.CharField(label="Text contains", required=False)
    year = forms.ChoiceField(label="Publication year", choices=YEARS)
    category = Museum_Multiple_Choice_Field(required=False, widget=forms.CheckboxSelectMultiple, choices=Article.CATEGORY_CHOICES, layout="multi-column")
    series = Enhanced_Model_Choice_Field(label="In Series", queryset=Series.objects.visible(), empty_label=FORM_ANY)
    sort = Museum_Select_Field(
        label="Sort results by",
        choices=Article_Sorter().get_sort_options_as_django_choices(),
        full_choices=Article_Sorter().get_sort_options_as_django_choices(include_all=True),
        required=False,
    )
