from django import forms
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

from museum_site.constants import HOST
from museum_site.core.misc import extract_file_key_from_url
from museum_site.fields import Enhanced_Model_Choice_Field
from museum_site.models import File, Collection, Collection_Entry
from museum_site.widgets import Collection_Title_Widget


class Collection_Form(forms.ModelForm):
    """ TODO: Currently only used with On The Fly Collections """
    use_required_attribute = False
    request = None
    attrs = {"method": "POST"}
    heading = "Create New Collection"
    submit_value = "Create Collection"

    class Meta:
        model = Collection
        fields = ["title", "short_description", "description", "visibility", "default_sort"]
        widgets = {"title": Collection_Title_Widget(char_limit=120)}

    def set_request(self, request): self.request = request

    def clean(self):
        cleaned_data = super().clean()

        if self.request is None:
            raise ValidationError("Form did not have request populated")

        # Check slug is available
        self.slug = slugify(self.cleaned_data["title"])
        if Collection.objects.duplicate_check(self.slug):
            raise ValidationError("Collection title already in use")

    def process(self):
        # Set the slug/user and save the collection
        c = self.save(commit=False)
        c.slug = self.slug
        c.user = self.request.user
        c.save()

    def response_success(self):
        return {"success": True}

    def response_failure(self):
        return {"success": False, "errors": self.errors.get_json_data()}


class Collection_Content_Form(forms.ModelForm):
    use_required_attribute = False
    request = None
    associated_file = Enhanced_Model_Choice_Field(
        widget=forms.RadioSelect(attrs={"class": "ul-scrolling-checklist"}),
        queryset=File.objects.all(),
        label="File To Add",
        required=False
    )
    url = forms.CharField(
        label="File URL",
        help_text="Alternatively paste a URL that contains a file's key rather than manually selecting from above. Has priority over any selection above.",
        required=False
    )

    collection_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Collection_Entry
        fields = ["associated_file", "url", "collection_description"]

    def set_request(self, request):
        self.request = request

    def clean_url(self):
        # Convert URL to zfile id
        url = self.cleaned_data["url"]
        if url == "":
            return url

        if not url.startswith(HOST):
            raise ValidationError("ERROR: Invalid url provided. Expecting - https://museumofzzt.com/file/&lt;action&gt;/&lt;key&gt;/")
        else:
            key = extract_file_key_from_url(url)
            if key is None:
                raise ValidationError("ERROR: Could not determine file key. Expecting - https://museumofzzt.com/file/&lt;action&gt;/&lt;key&gt;/")
            self.cleaned_data["associated_file"] = File.objects.get(key=key).pk
        return url

    def clean(self):
        cleaned_data = super().clean()

        if self.request is None:
            raise ValidationError("Form did not have request populated")

        # Confirm this is your collection
        c = Collection.objects.get(pk=cleaned_data.get("collection_id"))
        if self.request.user.id != c.user.id:
            raise ValidationError("You do not have permission to modify this collection.")

        # Check for duplicates
        duplicate = Collection_Entry.objects.duplicate_check(cleaned_data.get("collection_id"), cleaned_data.get("associated_file"))
        if duplicate:
            raise ValidationError("File already exists in collection!")

        self.collection_object = c

    def process(self):
        # Update collection item count
        self.collection_object.item_count += 1

        entry = Collection_Entry(
            collection_id=self.cleaned_data["collection_id"],
            zfile_id=self.cleaned_data["associated_file"],
            collection_description=self.cleaned_data["collection_description"],
            order=self.collection_object.item_count
        )

        # Save the collection entry
        entry.save()

        # Set the preview image if one isn't set yet
        if self.collection_object.preview_image is None:
            self.collection_object.preview_image = entry.zfile

        # Save the collection
        self.collection_object.save()

    def response_success(self):
        return {"success": True}

    def response_failure(self):
        return {"success": False, "errors": self.errors.get_json_data()}
