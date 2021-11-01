from django import forms
from .models import File, Upload
from .widgets import *

class ZGameForm(forms.ModelForm):
    #zfile = forms.FileField(help_text="Select the file you wish to upload. All uploads <i>must</i> be zipped.", label="File")
    zfile = forms.FileField(help_text="Select the file you wish to upload. All uploads <i>must</i> be zipped.", label="File", widget=UploadFileWidget())

    class Meta:
        model = File

        fields = [
            "zfile", "title", "author", "company", "genre", "release_date",
            "license",
            "description",
        ]

        help_texts = {
            "title": "Leave A/An/The as the first word if applicable.",
            "author": "Separate multiple authors with a comma. Do not abbreviate names. "
                      "For files with many authors, consider using the compiler as the author with \"Various\" to represent the rest.",
            "company": "The company this file is published under. If there is none, leave this field blank. If there are multiple, separate them with a comma.",
            "genre": "Check any applicable genres that describe the content of the uploaded file.",
            "release_date": "The date this file was first made public. If this is a new release, it should be the modified date of the most recent ZZT world (or executable, or other primary file). If the release date is not known, leave this field blank.",
            "license": "The license under which this world is published. If the license is unknown, leave this field blank.",
            "description": "An optional description of the upload. For utilities, please be sure to fill this out.",
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
            "genre": GenreCheckboxWidget(),
            "release_date": forms.DateInput(
                format=("%y-%m-%d"),
                attrs={"type": "date"}
            ),
            "zfile": UploadFileWidget(),
        }

class UploadForm(forms.ModelForm):
    generate_preview_image = forms.ChoiceField(
        help_text="Select a ZZT file whose title screen will be used for the world's preview image. Leave set to 'Automatic' to use the oldest file in the zip file. This image may be changed during publication. This option cannot be changed after upload.",
        choices=(("AUTO", "Automatic"), ("NONE", "Do Not Generate Preview Image"))
        )

    class Meta:
        model = Upload
        fields = ["generate_preview_image", "notes"]

        labels = {"notes": "Upload Notes"}

        help_texts = {
            "notes": "Notes for the uploader. Consider anything entered in this field to be public.",
        }
