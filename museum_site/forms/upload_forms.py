import time
import os
import zipfile

from datetime import datetime, timedelta, UTC

from django import forms
from django.utils.text import slugify

from museum_site.constants import LANGUAGES, LANGUAGE_CHOICES, UPLOAD_TEST_MODE, ZGAMES_BASE_PATH, PREVIEW_IMAGE_BASE_PATH
from museum_site.core.detail_identifiers import *
from museum_site.core.file_utils import calculate_md5_checksum
from museum_site.core.image_utils import optimize_image
from museum_site.core.misc import calculate_boards_in_zipfile, calculate_release_year, calculate_sort_title, get_letter_from_title, generate_screenshot_from_zip, record
from museum_site.fields import (
    Choice_Field_No_Validation, Tag_List_Field, Museum_Tagged_Text_Field, Museum_Choice_Field, Museum_Model_Scrolling_Multiple_Choice_Field,
    Museum_Multiple_Choice_Field, Museum_Scrolling_Multiple_Choice_Field, Museum_Drag_And_Drop_File_Field
)
from museum_site.models import Author, Company, Detail, Download, File, Genre, Upload, Zeta_Config
from museum_site.widgets import (
    Enhanced_Date_Widget, Enhanced_Text_Widget, Scrolling_Checklist_Widget, Tagged_Text_Widget, UploadFileWidget, Language_Checklist_Widget
)


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
    zeta_config = forms.ModelChoiceField(
        queryset=Zeta_Config.objects.filter(category__lte=1).order_by("category"),
        label="Configuration",
        help_text=(
            'Choose the intended configuration for playing the upload in the '
            'browser. If this upload cannot be ran with Zeta, select '
            '"Incompatible with Zeta". For the majority of ZZT worlds '
            '<span class="mono">`ZZT v3.2 (Registered)`</span> is the correct '
            'choice.'
        ),
        empty_label="Incompatible with Zeta",
        required=False,
        initial=1  # TODO Constant
    )


class Upload_Form(forms.ModelForm):
    generate_preview_image = Choice_Field_No_Validation(
        choices=[  # List rather than tuple so it can be modified later
            ("AUTO", "Automatic"),
            ("NONE", "None")
        ],
        help_text=(
            "Select a ZZT file whose title screen will be used for the world's "
            "preview image. Leave set to 'Automatic' to use the oldest file in "
            "the zip file. This image may be changed during publication."
        ),
        required=False
    )
    edit_token = forms.CharField(required=False, widget=forms.HiddenInput())
    announced = Museum_Choice_Field(
        label="Announce on Discord",
        widget=forms.RadioSelect(),
        choices=(
            (0, "Announce this upload"),
            (1, "Do not announce this upload")
        ),
        help_text=(
            "New uploads are automatically shared to the Discord of ZZT's "
            "announcements channel. You may choose to not announce the "
            "upload. The upload will still appear publically in the upload "
            "queue and on RSS feeds."
        ),
        initial=0,
        required=False
    )

    class Meta:
        model = Upload
        fields = ["generate_preview_image", "notes", "announced", "edit_token"]

        labels = {
            "generate_preview_image": "Preview image",
            "notes": "Upload notes",
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

    def process(self, ip, user_id=None):
        self.upload = self.save(commit=False)
        self.upload.generate_edit_token(force=False)
        self.upload.ip = ip
        self.upload.user_id = user_id
        self.upload.save()


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
        help_text="To confirm you have the correct upload and wish to delete it please type \"DELETE\" in the following text field.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["confirmation"].widget.attrs["placeholder"] = "DELETE"

    def clean_confirmation(self):
        if self.cleaned_data["confirmation"].upper() != "DELETE":
            self.add_error("confirmation", "You must provide confirmation before an upload can be deleted!")


class ZGame_Form(forms.ModelForm):
    UPLOAD_DIRECTORY = os.path.join(ZGAMES_BASE_PATH, "uploaded")
    mode = "new"

    field_order = ["zfile", "title", "author", "company", "genre", "explicit", "release_date", "language", "description"]
    zfile = Museum_Drag_And_Drop_File_Field(
        help_text=("Select the file you wish to upload. All uploads <i>must</i> be zipped."),
        label="File", widget=UploadFileWidget(target_text="Drag & Drop A Zip File Here or Click to Choose", allowed_preset="zip", show_size_limit=True)
    )
    # [Title]
    author = Museum_Tagged_Text_Field(
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
    )
    company = Museum_Tagged_Text_Field(
        required=False,
        help_text="Any companies this file is published under. If there are none, leave this field blank. If there are multiple, separate them with a comma.",
    )
    genre = Museum_Model_Scrolling_Multiple_Choice_Field(
        required=False,
        queryset=Genre.objects.visible(),
        widget=Scrolling_Checklist_Widget(buttons=["Clear"], show_selected=True),
        help_text=(
            "Check any applicable genres that describe the content of the uploaded file. Use 'Other' if a genre isn't represented and mention it in the upload"
            "notes field in the Upload Settings section. For a description of genres, see the <a href='/help/genre/' target='_blank'>Genre Overview</a> page."
        )
    )
    explicit = Museum_Choice_Field(
        widget=forms.RadioSelect(),
        choices=(
            (0, "This upload does not contain explicit content"),
            (1, "This upload contains explicit content")
        ),
        help_text=(
            "Check this box if the upload contains material not suitable for minors or non-consenting adults. "
            "Uploads marked as explicit require " "confirmation before accessing and never appear in Worlds of ZZT bot posts."
        ),
        initial=0
    )
    # [Release Date]
    language = Museum_Multiple_Choice_Field(required=False, widget=forms.CheckboxSelectMultiple, choices=LANGUAGE_CHOICES, layout="multi-column", help_text='For files in languages not specified here, use "Other". The language will be added after publication.')
    # [Description]

    use_required_attribute = False
    # Properties handled in view
    max_upload_size = 0
    editing = False
    expected_file_id = 0  # For replacing a zip

    uploaded_zipfile = None

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
        }

        widgets = {
            "title": Enhanced_Text_Widget(char_limit=80),
            "release_date": Enhanced_Date_Widget(buttons=["today", "clear"], clear_label="Unknown")
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

    def clean_company(self):
        company = self.cleaned_data["company"].replace(",", "/")

        if company.endswith("/"):
            company = company[:-1]

        return company

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

    def clean_release_date(self):
        current_release_date = self.cleaned_data["release_date"]
        cutoff = str(datetime.now(UTC) + timedelta(days=1))[:10]
        if str(current_release_date) > cutoff:
            raise forms.ValidationError("Invalid release date. Check your calendar.")
        return current_release_date

    def process(self):
        self.process_zgame_form()
        # Final save
        self.zfile.save()

        # Create a Download for zgames
        download, created = Download.objects.get_or_create(url="/zgames/uploaded/" + self.zfile.filename, kind="zgames")
        if created:
            self.zfile.downloads.add(download)

    def process_zgame_form(self):
        # Create the ZFile object intended to be saved to the database
        self.zfile = self.save(commit=False)  # FULLSAVE

        # If a zipfile was uploaded...
        if self.cleaned_data["zfile"]:
            if self.mode == "new":  # Set filename to the uploaded zipfile's if this is a new upload
                self.zfile.filename = self.cleaned_data["zfile"].name
            zfile_path = os.path.join(self.UPLOAD_DIRECTORY, self.zfile.filename)
            self.upload_submitted_zipfile(zfile_path)
            self.zfile.size = self.cleaned_data["zfile"].size
            self.zfile.checksum = calculate_md5_checksum(zfile_path)
            (self.zfile.playable_boards, self.zfile.total_boards) = calculate_boards_in_zipfile(zfile_path)

        self.zfile.letter = get_letter_from_title(self.zfile.title)

        if self.mode == "new":
            self.zfile.key = self.zfile.filename.lower()[:-4]
            self.zfile.release_source = "User upload"

        self.zfile.sort_title = calculate_sort_title(self.zfile.title)
        self.zfile.year = calculate_release_year(self.zfile.release_date)
        self.zfile.language = "/".join(self.cleaned_data["language"])
        self.zfile.save()
        self.zfile.details.add(Detail.objects.get(pk=DETAIL_UPLOADED))

        # Clear old many-to-many associations
        if self.mode == "edit":
            to_clear = ["genres", "companies", "authors"]
            for m2m in to_clear:
                self.clear_zfile_m2m(m2m)

        # Create new many-to-many associations
        for genre in self.cleaned_data["genre"]:
            self.zfile.genres.add(genre)

        for company in self.cleaned_data["company"].split("/"):
            if company == "":
                continue
            company_slug = slugify(company, allow_unicode=True)
            slug_exists = Company.objects.filter(slug=company_slug)
            if slug_exists:
                c_obj = slug_exists.first()
                self.zfile.companies.add(c_obj)
            else:
                (c_obj, created) = Company.objects.get_or_create(title=company.strip())
                self.zfile.companies.add(c_obj)
                if created:  # If it's newly created, set the slug
                    c_obj.generate_automatic_slug(save=True)

        for author in self.cleaned_data["author"].split("/"):
            if author == "":
                continue
            author_slug = slugify(author, allow_unicode=True)
            slug_exists = Author.objects.filter(slug=author_slug)
            if slug_exists:
                a_obj = slug_exists.first()
                self.zfile.authors.add(a_obj)
            else:
                (a_obj, created) = Author.objects.get_or_create(title=author.strip())
                self.zfile.authors.add(a_obj)
                if created:  # If it's newly created, set the slug
                    a_obj.generate_automatic_slug(save=True)

    def upload_submitted_zipfile(self, zfile_path):
        """ Move the uploaded zipfile to its destination directory """
        with open(zfile_path, 'wb+') as fh:
            for chunk in self.cleaned_data["zfile"].chunks():
                fh.write(chunk)

    def clear_zfile_m2m(self, m2m):
        """ Clears all associations with specified many to many field """
        getattr(self.zfile, m2m).clear()

    def generate_preview_image(self, requested_image_source="AUTO"):
        if requested_image_source == "NONE":
            # Remove existing screenshot if one exists
            if self.zfile.has_preview_image:
                os.remove(self.zfile.screenshot_phys_path())
                self.zfile.has_preview_image = False
            return True
        elif requested_image_source == "AUTO":
            if self.zfile.has_preview_image:
                return True  # Keep existing preview image
            requested_image_source = None  # Provide no specific world when generating the image

        # Generate a new image
        screenshot_filename = self.zfile.key + ".png"
        screenshot_path = os.path.join(PREVIEW_IMAGE_BASE_PATH, self.zfile.bucket(), screenshot_filename)
        if generate_screenshot_from_zip(self.zfile.phys_path(), screenshot_path, world=requested_image_source):
            self.zfile.has_preview_image = True
            optimize_image(self.zfile.screenshot_phys_path())
        return True
