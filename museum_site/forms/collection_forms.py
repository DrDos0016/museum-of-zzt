from django import forms

from museum_site.fields import Enhanced_Model_Choice_Field
from museum_site.models import File, Collection, Collection_Entry


class Collection_Content_Form(forms.ModelForm):
    use_required_attribute = False
    associated_file = Enhanced_Model_Choice_Field(
        widget=forms.RadioSelect(attrs={"class": "ul-scrolling-checklist"}),
        queryset=File.objects.all(),
        label="File To Add",
    )
    url = forms.CharField(
        label="File URL",
        help_text="Alternatively paste a URL that contains a file's key rather than manually selecting from above. Has priority over any selection above."
    )

    collection_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Collection_Entry
        fields = ["associated_file", "url", "collection_description"]
