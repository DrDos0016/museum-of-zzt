import zipfile

from django import forms

from museum_site.constants import LANGUAGES, LANGUAGE_CHOICES, UPLOAD_TEST_MODE
from museum_site.core.misc import record
from museum_site.fields import Tag_List_Field
from museum_site.models import Download, File, Genre, Upload, Zeta_Config
from museum_site.widgets import Enhanced_Date_Widget, Enhanced_Text_Widget, Scrolling_Checklist_Widget, Tagged_Text_Widget, UploadFileWidget


class Download_Form(forms.ModelForm):
    use_required_attribute = False
    url = forms.URLField(
        required=False,
        label="URL",
        help_text=(
            "An alternate location to acquire this file. The link "
            "should lead to an active page where the file can be downloaded "
            "<b>not</b> a direct link to the hosted file. The URL should "
            "direct to a webpage with an official release by the file's "
            "author, not an alternative ZZT archive, the Internet Archive, or "
            "any unmaintained webpage."
        )
    )

    class Meta:
        model = Download
        fields = ["url", "kind", "hosted_text"]

        labels = {"url": "URL", "kind": "Category"}

        help_texts = {
            "kind": "The type of webpage this file is hosted on. This is used to determine an icon to display when selecting an alternate download source.",
            "hosted_text": (
                "For non-Itch download sources only. On the file's downloads page, the text entered here will be prefixed with &quot;Hosted on&quot;."
            ),
        }

    def __init__(self, data=None, initial={}, instance=None):
        super().__init__(data, initial=initial, instance=instance)
        self.fields["kind"].widget.choices = self.fields["kind"].widget.choices[1:]  # Remove "zgames" as a possible alterante download location


class Play_Form(forms.Form):
    zeta_config = forms.ChoiceField(
        choices=Zeta_Config.objects.select_list(),
        label="Configuration",
        help_text=(
            'Choose the intended configuration for playing the upload in the '
            'browser. If this upload cannot be ran with Zeta, select '
            '"Incompatible with Zeta" at the end of the list. For the vast '
            'majority of ZZT worlds "ZZT v3.2 (Registered)" is the correct '
            'choice.'
        )
    )


class Upload_Form(forms.ModelForm):
    generate_preview_image = forms.ChoiceField(
        choices=[  # List rather than tuple so it can be modified later
            ("AUTO", "Automatic"),
            ("NONE", "None")
        ],
        help_text=(
            "Select a ZZT file whose title screen will be used for the world's "
            "preview image. Leave set to 'Automatic' to use the oldest file in "
            "the zip file. This image may be changed during publication."
        ),

    )
    edit_token = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Upload
        fields = ["generate_preview_image", "notes", "announced", "edit_token"]

        labels = {
            "generate_preview_image": "Preview image",
            "notes": "Upload notes",
            "announced": "Announce on Discord",
            }

        help_texts = {
            "notes": (
                "Notes for staff to read before publication such as special "
                "instructions before publishing. While not visible to users on "
                "the site directly, consider anything entered in this field to "
                "be public."
            ),
            "announced": (
                "New uploads are automatically shared to the Discord of ZZT's "
                "announcements channel. You may choose to not announce the "
                "upload. The upload will still appear publically in the upload "
                "queue and on RSS feeds."
            ),
        }

        widgets = {
            "announced": forms.RadioSelect(
                choices=(
                    (0, "Announce this upload"),
                    (1, "Do not announce this upload")
                ),
            ),
        }


class Upload_Action_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Select Upload"

    token = forms.CharField(max_length=16)
    action = forms.CharField(max_length=8, widget=forms.HiddenInput())


class Upload_Delete_Confirmation_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Delete This Upload"
    attrs = {"method": "POST"}

    confirmation = forms.CharField(
        max_length=6,
        help_text="To confirm you have the correct upload and wish to delete it please type \"DELETE\" in the following text input.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["confirmation"].widget.attrs["placeholder"] = "DELETE"

    def clean_confirmation(self):
        if self.cleaned_data["confirmation"].upper() != "DELETE":
            self.add_error("confirmation", "You must provide confirmation before an upload can be deleted!")


class ZGame_Form(forms.ModelForm):
    field_order = ["zfile", "title", "author", "company", "genre", "explicit", "release_date", "language", "description"]
    zfile = forms.FileField(
        help_text=("Select the file you wish to upload. All uploads <i>must</i> be zipped."),
        label="File", widget=UploadFileWidget(target_text="Drag & Drop A Zip File Here or Click to Choose", allowed_filetypes=".zip,application/zip")
    )
    company = Tag_List_Field(
        widget=Tagged_Text_Widget(suggestion_key="company"),
        required=False,
        help_text=("Any companies this file is published under. If there are none, leave this field blank. If there are multiple, separate them with a comma."),
    )
    genre = forms.ModelMultipleChoiceField(
        widget=Scrolling_Checklist_Widget(buttons=["Clear"], show_selected=True),
        queryset=Genre.objects.visible(),
        required=False,
        help_text=(
            "Check any applicable genres that describe the content of the uploaded file. Use 'Other' if a genre isn't represented and mention it in the upload"
            "notes field in the Upload Settings section. For a description of genres, see the <a href='/help/genre/' target='_blank'>Genre Overview</a> page."
        )
    )
    author = forms.CharField(
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
        widget=Tagged_Text_Widget(),
    )
    language = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(
            choices=LANGUAGE_CHOICES,
            buttons=["Clear"],
            show_selected=True,
        ),
        choices=LANGUAGE_CHOICES,
        required=False,
        help_text=(
            'Check any languages the player is expected to understand to comprehend the files in the upload. For worlds exclusively using created languages,'
            'use "Other". If a language is not listed, use "Other" and specify the correct language in the upload notes section.'
        )
    )

    use_required_attribute = False
    # Properties handled in view
    max_upload_size = 0
    editing = False
    expected_file_id = 0  # For replacing a zip

    class Meta:
        model = File

        fields = ["zfile", "title", "explicit", "release_date", "description"]

        help_texts = {
            "title": "Leave A/An/The as the first word if applicable.",
            "release_date": (
                "Enter the date this file was first made public. If this is a "
                "newly created file, it should be today's date. If this is an "
                "older release being uploaded now, it should be the "
                "modification date of the most "
                "recent ZZT world (or executable, or other primary file). If "
                "the release date is not known, select \"Unknown\" to leave "
                "this field blank."
            ),
            "release_source": (
                "Where the data for the release date is coming from"
            ),
            "description": (
                "A description for the uploaded file. For utilities, please "
                "be sure to fill this out. If the description is written by "
                "the file's author, and not a third party please wrap it in "
                "quotation marks."
            ),
            "explicit": (
                "Check this box if the upload contains material not suitable "
                "for minors or non-consenting adults. Uploads marked as "
                "explicit will require confirmation before accessing and "
                "never appear in Worlds of ZZT bot posts."
            ),
        }

        widgets = {
            "title": Enhanced_Text_Widget(char_limit=80),
            "explicit": forms.RadioSelect(
                choices=(
                    (0, "This upload does not contain explicit content"),
                    (1, "This upload contains explicit content")
                ),
            ),
            "release_date": Enhanced_Date_Widget(buttons=["today", "clear"], clear_label="Unknown"),
            "zfile": UploadFileWidget(),
        }

    def clean_zfile(self):
        zfile = self.cleaned_data["zfile"]
        if zfile is None:
            return zfile

        # Coerce successful upload when testing on DEV
        if UPLOAD_TEST_MODE:
            record("UPLOAD_TEST_MODE: Bypassing clean_zfile()")
            zfile.name = str(int(time.time())) + "-" + zfile.name

        # Check uploaded file is a zip
        if zfile and (not zfile.name.lower().endswith(".zip")):  # Ensure proper extension
            raise forms.ValidationError("Only zip files may be uploaded. Please zip your upload and try again.")
        elif zfile and not zipfile.is_zipfile(zfile):  # Attempt to confirm the zip is legitimate
            raise forms.ValidationError("Uploaded file is not a valid zip file.")

        # Check for a duplicate filename, but make sure its ID isn't the same as this upload's
        if zfile and zfile.name:
            dupe = File.objects.filter(filename=zfile.name).first()
            if dupe and dupe.id != self.expected_file_id:
                raise forms.ValidationError("The selected filename is already in use. Please rename your zipfile.")

        # Check maximum upload size
        if zfile and zfile.size > self.max_upload_size:
            raise forms.ValidationError("File exceeds your maximum upload size! Contact Dr. Dos for a manual upload.")

        return zfile

    def clean_author(self):
        author = self.cleaned_data["author"].replace(",", "/")

        if author.endswith("/"):
            author = author[:-1]

        # Replace blank authors with "Unknown"
        if author == "":
            author = "Unknown"

        return author

    def clean_genre(self):
        if UPLOAD_TEST_MODE:
            record("UPLOAD_TEST_MODE: Bypassing clean_genre()")
            if len(self.cleaned_data["genre"]) == 0:
                record("UPLOAD_TEST_MODE: Setting genre to 'Adventure'")
                self.cleaned_data["genre"].append("3")  # Adventure TODO: Constant?
                return self.cleaned_data["genre"]

        # Make sure all requested genres exist
        valid_genres = list(Genre.objects.filter(visible=True).values_list("id", flat=True))
        to_add = []

        if len(self.cleaned_data["genre"]):
            for genre in self.cleaned_data["genre"]:
                if int(genre.pk) not in valid_genres:
                    raise forms.ValidationError("An invalid genre was specified.")
                # Some genres imply others -- TODO make these constants
                if int(genre.pk) in [1, 8, 29, 61, 62] and 16 not in to_add:  # 1:24HoZ, 8:BK, 16:Contest, 29:Ludum, 61:WoZZT, 62:Oktroll
                    to_add.append(16)  # Contest
        else:
            raise forms.ValidationError("At least one genre must be specified.")

        return list(self.cleaned_data["genre"]) + to_add

    def clean_language(self):
        if UPLOAD_TEST_MODE:
            record("UPLOAD_TEST_MODE: Bypassing clean_language()")
            if len(self.cleaned_data["language"]) == 0:
                self.cleaned_data["language"].append("en")  # English TODO: Constant?
                return self.cleaned_data["language"]

        # Make sure all requested languages exist
        valid_languages = list(LANGUAGES.keys())

        if len(self.cleaned_data["language"]):
            for language in self.cleaned_data["language"]:
                if language not in valid_languages:
                    raise forms.ValidationError("An invalid language was specified.")
        else:
            raise forms.ValidationError("At least one language must be specified.")
        return self.cleaned_data["language"]
