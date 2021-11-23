from django import forms
from .models import File, Upload, Zeta_Config, Download
from .widgets import *
from .common import GENRE_LIST
from .constants import LICENSE_CHOICES, LICENSE_SOURCE_CHOICES, LANGUAGE_CHOICES


class ZGameForm(forms.ModelForm):
    zfile = forms.FileField(help_text="Select the file you wish to upload. All uploads <i>must</i> be zipped.", label="File", widget=UploadFileWidget())

    use_required_attribute = False
    max_upload_size = 0  # Properly set this value in a view

    class Meta:
        model = File

        fields = [
            "zfile", "title", "author", "company", "genre", "explicit",
            "release_date", "language",
            "description",
        ]

        help_texts = {
            "title": "Leave A/An/The as the first word if applicable.",
            "author": "Separate multiple authors with a comma. Do not abbreviate names. "
                      "For files with many authors, consider using the compiler as the author with \"Various\" to represent the rest.",
            "company": "The company this file is published under. If there is none, leave this field blank. If there are multiple, separate them with a comma.",
            "genre": "Check any applicable genres that describe the content of the uploaded file.",
            "release_date": "Enter the date this file was first made public. If this is a new release, it should be the modified date of the most recent ZZT world (or executable, or other primary file). If the release date is not known, leave this field blank.",
            "release_source": "Where the data for the release date is coming from",
            "language": 'Check any languages the player is expected to understand to comprehend the files in the upload. For worlds exclusively using created languages, use "Other".',
            "license": "The license under which this world is published.",
            "license_source": "Where the license can be found. Use a source contained within the uploaded file when possible.",
            "description": "An optional description of the upload. For utilities, please be sure to fill this out.",
            "explicit": "Check this box if the upload contains material not suitable for minors or non-consenting adults. Uploads marked as explicit will require confirmation before accessing and never appear in Worlds of ZZT bot posts.",
        }

        widgets = {
            "author": SlashSeparatedValueWidget(
                attrs={
                    "list": "author-suggestions",
                    "autocomplete": "off",
                    }
            ),
            "company": SlashSeparatedValueWidget(
                attrs={
                    "list": "company-suggestions",
                    "autocomplete": "off",
                    }
            ),
            "genre": SlashSeparatedValueCheckboxWidget(
                choices=list(zip(GENRE_LIST, GENRE_LIST))
            ),
            "explicit": forms.RadioSelect(
                choices=((0, "This upload does not contain explicit content"), (1, "This upload contains explicit content")),
            ),
            "release_date": forms.DateInput(
                format=("%y-%m-%d"),
                attrs={"type": "date"}
            ),
            "language": SlashSeparatedValueCheckboxWidget(
                choices=LANGUAGE_CHOICES,
            ),
            "license": SelectPlusCustomWidget(
                choices=LICENSE_CHOICES
            ),
            "license_source": SelectPlusCustomWidget(
                choices=LICENSE_SOURCE_CHOICES
            ),
            "zfile": UploadFileWidget(),
        }

    def clean_zfile(self):
        zfile = self.cleaned_data["zfile"]

        if zfile.size > self.max_upload_size:
            raise forms.ValidationError("File exceeds your maximum upload size! Contact Dr. Dos for a manual upload.")


class PlayForm(forms.Form):
    zeta_config = forms.ChoiceField(choices=Zeta_Config.objects.select_list(), label="Configuration", help_text='Choose the intended configuration for playing the upload in the browser. If this upload cannot be ran with Zeta, select "Incompatible with Zeta" at the end of the list. For the vast majority of ZZT worlds "ZZT v3.2R" is the correct choice.' )


class UploadForm(forms.ModelForm):
    generate_preview_image = forms.ChoiceField(
        help_text="Select a ZZT file whose title screen will be used for the world's preview image. Leave set to 'Automatic' to use the oldest file in the zip file. This image may be changed during publication. This option cannot be changed after upload.",
        choices=[("AUTO", "Automatic"), ("NONE", "Do Not Generate Preview Image")]  # Must be a list to be added to later
        )

    class Meta:
        model = Upload
        fields = ["generate_preview_image", "notes", "announced"]

        labels = {
            "generate_preview_image": "Preview image",
            "notes": "Upload notes",
            "announced": "Announce on Discord",
            }

        help_texts = {
            "notes": "Notes for staff to read before publication such as special instructions before publishing. While not visible to users on the site directly, consider anything entered in this field to be public.",
            "announced": "New uploads are automatically shared to the Discord of ZZT's announcements channel. You may choose to not announce the upload. The upload will still appear publically in the upload queue and on RSS feeds.",
        }

        widgets = {
            "announced": forms.RadioSelect(
                choices=((0, "Announce this upload"), (1, "Do not announce this upload")),
            )
        }


class DownloadForm(forms.ModelForm):
    use_required_attribute = False
    url = forms.URLField(required=False, label="URL", help_text="An alternate location to acquire this file. The link should lead to an active page where the file can be downloaded <b>not</b> a direct link to the hosted file. The URL should direct to a webpage with an official release by the file's author, not an alternative ZZT archive, the Internet Archive, or a defunct but still online webpage.")

    class Meta:
        model = Download
        fields = ["url", "kind"]

        labels = {
            "url": "URL",
            "kind": "Category",
        }

        help_texts = {
            "kind": "The type of webpage this file is hosted on. This is used to determine an icon to display when selecting an alternate download source."
        }
