from django import forms


from museum_site.models import File, Collection, Collection_Entry


def associated_file_choices(query="all"):
    """ TODO Use a ModelChoiceField  instead of this """
    raw = getattr(File.objects, query)().only("id", "title", "key")
    choices = []
    for i in raw:
        choices.append((i.id, "{} [{}]".format(i.title, i.key)))
    return choices

class Collection_Content_Form(forms.ModelForm):
    use_required_attribute = False
    associated_file = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={"class": "ul-scrolling-checklist"}),
        choices=associated_file_choices,
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

