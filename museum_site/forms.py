import glob
import os
import time
import zipfile

from datetime import datetime, timedelta, timezone

from django import forms
from django.urls import reverse_lazy
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.template.defaultfilters import linebreaks, urlize
from django.template.loader import render_to_string

from PIL import Image
from internetarchive import upload as ia_upload

from museum_site.core import *
from museum_site.common import record
from museum_site.constants import (
    LICENSE_CHOICES, LICENSE_SOURCE_CHOICES, LANGUAGE_CHOICES, TERMS, UPLOAD_TEST_MODE, SITE_ROOT, TEMP_PATH, YEAR, EMAIL_ADDRESS
)
from museum_site.core.detail_identifiers import *
from museum_site.core.file_utils import delete_this
from museum_site.core.form_utils import any_plus, get_sort_option_form_choices
from museum_site.fields import *
from museum_site.models import *
from museum_site.private import IA_ACCESS, IA_SECRET
from museum_site.widgets import *


STUB_CHOICES = (("A", "First"), ("B", "Second"), ("C", "Third"))  # For debugging

PREVIEW_IMAGE_CROP_CHOICES = (
    ("ZZT", "480x350 ZZT Board"),
    ("SZZT", "448x400 Super ZZT Board"),
    ("NONE", "Do Not Crop Image"),
)

# Common strings
PASSWORD_HELP_TEXT = "Use a unique password for your account with a minimum length of <b>8</b> characters. Passwords are hashed and cannot be viewed by staff."
PATRON_DISCLAIMER_TEXT = (
    "This data isn't parsed in any way, so you may write anything you like as long as it can be understood by <a href='mailto:{}'>Dr. Dos</a>.<br><br> "
    "If your suggestion cannot be used for whatever reason (due to an author's request or some other conflict) you will be contacted. Selections will be "
    "used in the order they appear here if applicable."
)


class ZGameForm(forms.ModelForm):
    field_order = ["zfile", "title", "author", "company", "genre", "explicit", "release_date", "language", "description"]
    zfile = forms.FileField(
        help_text=("Select the file you wish to upload. "
                   "All uploads <i>must</i> be zipped."),
        label="File", widget=UploadFileWidget(target_text="Drag & Drop A Zip File Here or Click to Choose", allowed_filetypes=".zip,application/zip")
    )
    company = Tag_List_Field(
        widget=Tagged_Text_Widget(suggestion_key="company"),
        required=False,
        help_text=("Any companies this file is published under. If there are none, leave this field blank. If there are multiple, separate them with a comma."),
    )
    genre = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(choices=qs_to_select_choices(Genre.objects.filter(visible=True)), buttons=["Clear"], show_selected=True),
        choices=qs_to_select_choices(Genre.objects.filter(visible=True)),
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
                raise forms.ValidationError(
                    "The selected filename is already in use. Please rename your zipfile."
                )

        # Check maximum upload size
        if zfile and zfile.size > self.max_upload_size:
            raise forms.ValidationError(
                "File exceeds your maximum upload size! Contact Dr. Dos for a manual upload."
            )

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

        if len(self.cleaned_data["genre"]):
            for genre in self.cleaned_data["genre"]:
                if int(genre) not in valid_genres:
                    raise forms.ValidationError("An invalid genre was specified.")
        else:
            raise forms.ValidationError("At least one genre must be specified.")
        return self.cleaned_data["genre"]

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


class PlayForm(forms.Form):
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


class UploadForm(forms.ModelForm):
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


class DownloadForm(forms.ModelForm):
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

        labels = {
            "url": "URL",
            "kind": "Category",
        }

        help_texts = {
            "kind": (
                "The type of webpage this file is hosted on. This is used to "
                "determine an icon to display when selecting an alternate "
                "download source."
            ),
            "hosted_text": (
                "For non-Itch download sources only. On the file's downloads "
                "page, the text entered here will be prefixed with "
                "\"Hosted on\"."
            ),
        }


class Advanced_Search_Form(forms.Form):
    use_required_attribute = False
    heading = "Advanced Search"
    attrs = {"method": "GET"}
    submit_value = "Search Files"
    manual_fields = ["board", "rating", "associated"]

    title = forms.CharField(label="Title contains", required=False)
    author = forms.CharField(label="Author contains", required=False)
    filename = forms.CharField(label="Filename contains", required=False)
    contents = forms.CharField(label="Zip file contents contains", help_text="Enter a filename to search for in the file's zip file", required=False)
    company = forms.CharField(label="Company contains", required=False)
    genre = forms.ChoiceField(
        choices=qs_to_select_choices(Genre.objects.filter(visible=True).only("pk", "title", "slug"), allow_any=True, val="{0.title}"),
        required=False,
    )
    board = Manual_Field(
        label="Minimum / Maximum board count",
        widget=Board_Range_Widget(min_val=0, max_val=999, max_length=3),
        required=False,
    )
    year = forms.ChoiceField(
        label="Release year",
        choices=range_select_choices(1991, YEAR, allow_any=True, allow_unknown=True, order="desc"),
        required=False,
    )
    rating = Manual_Field(
        label="Minimum / Maximum rating",
        widget=Range_Widget(min_val=0, max_val=5, max_length=4, step=0.1, include_clear=True),
        required=False,
        help_text="User input must be a number ranging from 0.0 to 5.0"
    )
    lang = forms.ChoiceField(
        label="Language",
        choices=language_select_choices(LANGUAGES, allow_any=True, allow_non_english=True),
        required=False,
    )
    associated = Manual_Field(
        label="Related content",
        widget=Associated_Content_Widget(),
        required=False,
    )
    details = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(
            choices=qs_to_categorized_select_choices(
                Detail.objects.filter(visible=True),
                category_order=["ZZT", "SZZT", "Media", "Other"]
            ),
            categories=True,
            buttons=["Clear", "Default"],
            show_selected=True,
            default=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED, DETAIL_WEAVE]
        ),
        choices=qs_to_categorized_select_choices(Detail.objects.filter(visible=True), category_order=["ZZT", "SZZT", "Media", "Other"]),
        required=False,
    )
    sort = forms.ChoiceField(
        label="Sort results by",
        choices=(
            ("title", "Title"),
            ("author", "Author"),
            ("company", "Company"),
            ("rating", "Rating"),
            ("release", "Release Date"),
        ),
        required=False,
    )

    def __init__(self, data=None, initial={}):
        super().__init__(data, initial=initial)
        for field in self.manual_fields:
            self.fields[field].widget.manual_data = self.data.copy()  # Copy to make mutable
            # Coerce specific min/max inputs to generic min/max keys
            self.fields[field].widget.manual_data["min"] = self.fields[field].widget.manual_data.get(field + "_min")
            self.fields[field].widget.manual_data["max"] = self.fields[field].widget.manual_data.get(field + "_max")

    def clean_board(self):
        return self.clean_range("board", 0, 999, "Minimum board count is larger than maximum board count")

    def clean_rating(self):
        return self.clean_range("rating", 0, 5, "Minimum rating is larger than maximum rating")

    def clean_range(self, field_name, allowed_min, allowed_max, error_message):
        requested_min = self.data.get(field_name + "_min", allowed_min)
        requested_max = self.data.get(field_name + "_max", allowed_max)

        if requested_min != "" or requested_max != "":
            if requested_min == "":
                requested_min = allowed_min
            if requested_max == "":
                requested_max = allowed_max
            requested_min = float(requested_min)
            requested_max = float(requested_max)

            if requested_max < requested_min:
                self.add_error(field_name, error_message)

        return []


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

    # TODO this may need to be moved/replaced if DB model changes
    CATEGORIES = Article.CATEGORY_CHOICES

    SERIES_CHOICES = [("Any", "- ANY -")] + list(
        Series.objects.filter(visible=True).order_by("title").values_list(
            "id", "title"
        )
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
    category = forms.MultipleChoiceField(
        required=False, widget=forms.CheckboxSelectMultiple, choices=CATEGORIES
    )
    series = forms.ChoiceField(label="In Series", choices=SERIES_CHOICES)
    sort = forms.ChoiceField(choices=SORTS)


class MirrorForm(forms.Form):
    use_required_attribute = False
    required = False

    IA_LANGUAGES = (
        ("dan", "Danish"),
        ("dut", "Dutch"),
        ("eng", "English"),
        ("fre", "French"),
        ("ger", "German"),
        ("ita", "Italian"),
        ("nor", "Norwegian"),
        ("pol", "Polish"),
        ("spa", "Spanish"),
    )

    COLLECTIONS = (
        ("test_collection", "Test Collection - Removed in 30 days"),
        ("open_source_software", "Software"),
    )

    PACKAGES = (
        # :: is a delimiter for JS to set launch command for main EXE
        ("RecOfZZT.zip", "The Reconstruction of ZZT::ZZT.EXE"),
        ("RecSZZT.zip", "The Reconstruction of Super ZZT::SUPERZ.EXE"),
        ("czoo421-dos.zip", "ClassicZoo v4.21::ZZT.EXE"),
        ("sczo404.zip", "Super ClassicZoo v4.04::SUPERZ.EXE"),
    )

    title = forms.CharField(label="Title")
    url = forms.CharField(
        label="URL", help_text="File will being uploaded to /details/[url]"
    )
    filename = forms.CharField(help_text="Filename for the upload")
    creator = forms.CharField(
        label="Creator", help_text="Separate with semicolons"
    )
    year = forms.IntegerField(label="Year", required=False)
    subject = forms.CharField(
        label="Subject", help_text="Separate with semicolons"
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(),
        help_text="Can contain links, formatting and images in html/css"
    )
    collection = forms.ChoiceField(choices=COLLECTIONS)
    language = forms.ChoiceField(choices=IA_LANGUAGES, initial="eng")
    zfile = forms.FileField(
        required=False,
        help_text=("Alternative zipfile to use instead of the Museum's copy"),
        label="Alternate Zip",
        widget=UploadFileWidget()
    )
    packages = forms.MultipleChoiceField(
        required=False, widget=forms.CheckboxSelectMultiple, choices=PACKAGES,
        help_text="Additional zipfiles whose contents are to be included"
    )
    default_world = forms.ChoiceField(required=False, choices=[])
    launch_command = forms.CharField(required=False)
    zzt_config = forms.CharField(
        required=False,
        label="ZZT.CFG Contents",
        help_text="Leave blank to not include this file",
        widget=forms.Textarea(),
        initial="REGISTERED"
    )

    def mirror(self, zfile, files=None):
        archive_title = self.cleaned_data["title"]
        # Copy the file's zip into a temp directory
        if self.cleaned_data["collection"] == "test_collection":
            ts = str(int(time.time()))
            wip_zf_name = "test_" + ts + "_" + self.cleaned_data["filename"]
            archive_title = "Test - " + ts + "_" + archive_title
            url = "test_" + ts + "_" + self.cleaned_data["url"]
            print(url)
        else:
            wip_zf_name = self.cleaned_data["filename"]
            url = self.cleaned_data["url"]

        wip_dir = os.path.join(TEMP_PATH, os.path.splitext(wip_zf_name)[0])
        wip_zf_path = os.path.join(wip_dir, wip_zf_name)
        try:
            os.mkdir(wip_dir)
        except FileExistsError:
            pass

        # Create a ZZT.CFG if parameters were specified
        if self.cleaned_data["zzt_config"]:
            with open(os.path.join(wip_dir, "ZZT.CFG"), "w") as fh:
                fh.write(self.cleaned_data["zzt_config"])

        # Extract zfile if not using an alternate zip
        if self.cleaned_data["zfile"]:
            zf = zipfile.ZipFile(files["zfile"])
        else:
            zf = zipfile.ZipFile(zfile.phys_path())

        files = zf.infolist()
        comment = zf.comment
        for f in files:
            zf.extract(f, path=wip_dir)
            timestamp = time.mktime(f.date_time + (0, 0, -1))
            os.utime(os.path.join(wip_dir, f.filename), (timestamp, timestamp))
        zf.close()

        # Extract any additional packages
        for package in self.cleaned_data["packages"]:
            package_path = os.path.join(
                SITE_ROOT, "museum_site", "static", "data", "ia_packages",
                package
            )
            zf = zipfile.ZipFile(package_path)
            files = zf.infolist()
            for f in files:
                zf.extract(f, path=wip_dir)
                timestamp = time.mktime(f.date_time + (0, 0, -1))
                os.utime(
                    os.path.join(wip_dir, f.filename), (timestamp, timestamp)
                )
            zf.close()

        # Add to WIP archive
        package_files = glob.glob(os.path.join(wip_dir, "*"))
        zf = zipfile.ZipFile(wip_zf_path, "w")
        for f in package_files:
            if os.path.basename(f) != wip_zf_name:
                zf.write(f, arcname=os.path.basename(f))
        if comment:
            zf.comment = comment
        zf.close()

        # Zip file is in its proper state, proceed to upload:
        meta = {
            "title": archive_title,
            "mediatype": "software",
            "collection": self.cleaned_data["collection"],
            "emulator": "dosbox",
            "emulator_ext": "zip",
            "emulator_start": self.cleaned_data["launch_command"],
            "subject": self.cleaned_data["subject"],
            "creator": self.cleaned_data["creator"].split(";"),
            "description": self.cleaned_data["description"]
        }

        if self.cleaned_data["year"] is not None:
            meta["year"] = str(self.cleaned_data["year"])

        # Mirror the file
        r = ia_upload(
            url,
            files=[wip_zf_path],
            metadata=meta,
            access_key=IA_ACCESS,
            secret_key=IA_SECRET,
        )

        # Remove the working files/folders
        delete_this(wip_dir)
        return r


class ReviewForm(forms.ModelForm):
    RATINGS = (
        (-1, "No rating"), (0, "0.0"), (0.5, "0.5"), (1.0, "1.0"), (1.5, "1.5"), (2.0, "2.0"),
        (2.5, "2.5"), (3.0, "3.0"), (3.5, "3.5"), (4.0, "4.0"), (4.5, "4.5"), (5.0, "5.0"),
    )

    use_required_attribute = False
    rating = forms.ChoiceField(
        choices=RATINGS,
        help_text="Optionally provide a numeric score from 0.0 to 5.0",
    )

    class Meta:
        model = Review
        fields = ["author", "title", "content", "rating"]

        labels = {
            "title": "Review Title",
            "author": "Your Name",
            "content": "Review",
        }

        help_texts = {
            "content": (
                '<a href="http://daringfireball.net/projects/markdown/syntax" '
                'target="_blank" tabindex="-1">Markdown syntax</a> is '
                'supported for formatting.'
            ),
        }

    def clean_author(self):
        # Replace blank authors with "Unknown"
        author = self.cleaned_data["author"]

        if author == "" or author.lower() == "n/a":
            author = "Anonymous"

        if author.find("/") != -1:
            raise forms.ValidationError(
                "Author may not contain slashes."
            )

        return author


class Review_Search_Form(forms.ModelForm):
    RATINGS = (
        (0, "0.0"),
        (0.5, "0.5"),
        (1.0, "1.0"),
        (1.5, "1.5"),
        (2.0, "2.0"),
        (2.5, "2.5"),
        (3.0, "3.0"),
        (3.5, "3.5"),
        (4.0, "4.0"),
        (4.5, "4.5"),
        (5.0, "5.0"),
    )

    heading = "Review Search"
    attrs = {
        "method": "GET",
        "action": reverse_lazy("review_directory")
    }
    submit_value = "Search Reviews"

    # Fields
    use_required_attribute = False
    review_date = forms.ChoiceField(
        label="Year Reviewed",
        choices=any_plus(((str(x), str(x)) for x in range(YEAR, 2001, -1)))  # Earliest review is from 2002
    )
    min_rating = forms.ChoiceField(label="Minimum Rating", choices=RATINGS)
    max_rating = forms.ChoiceField(label="Maximum Rating", choices=RATINGS, initial=5.0)
    ratingless = forms.BooleanField(label="Include Reviews Without Ratings", initial=True)
    sort = forms.ChoiceField(label="Sort Results By", choices=get_sort_option_form_choices(Review.sort_options))

    class Meta:
        model = Review
        fields = ["title", "author", "content"]

        labels = {
            "title": "Title Contains",
            "author": "Author Contains",
            "content": "Text Contains",
        }

        widgets = {
            "content": forms.TextInput()
        }


class SeriesForm(forms.ModelForm):
    user_required_attribute = False
    attrs = {
        "method": "POST",
        "enctype": "multipart/form-data",
    }
    submit_value = "Add Series"

    associations = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(
            choices=qs_to_categorized_select_choices(
                Article.objects.not_removed(),
            ),
        ),
        choices=list(Article.objects.not_removed().values_list("id", "title")),
        required=False,
        label="Associated Articles"
    )
    preview = forms.FileField(
        help_text="Select the image you wish to upload.",
        label="Preview Image", widget=UploadFileWidget(target_text="Drag & Drop Image Here or Click to Choose", allowed_filetypes=".png,image/png")
    )
    crop = forms.ChoiceField(label="Preview Image Crop", choices=PREVIEW_IMAGE_CROP_CHOICES)

    class Meta:
        model = Series
        fields = ["title", "description", "visible"]


def associated_file_choices(query="all"):
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


class Zeta_Advanced_Form(forms.Form):
    use_required_attribute = False
    zeta_config = forms.ChoiceField(choices=(("A", "A"), ("B", "B"), ("C", "C")))
    zeta_disable_params = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=STUB_CHOICES
    )
    executable = forms.ChoiceField(choices=(("A", "A"), ("B", "B"), ("C", "C")))
    blink_duration = forms.IntegerField()
    charset_override = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=STUB_CHOICES
    )
    buffer_size = forms.IntegerField()
    sample_rate = forms.IntegerField()
    note_delay = forms.IntegerField()
    volume = forms.IntegerField()
    included_zfiles = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=STUB_CHOICES
    )
    show_again = forms.BooleanField()


class Livestream_Description_Form(forms.Form):
    heading = "Livestream Description Generator"
    use_required_attribute = False
    submit_value = "Select"
    associated = forms.MultipleChoiceField(
        widget=Ordered_Scrolling_Radio_Widget(choices=associated_file_choices()),
        choices=associated_file_choices(),
        label="Associated ZFiles",
        help_text="Select one or more ZFiles",
        required=False,
    )
    stream_date = forms.CharField(
        widget=forms.DateInput(
            format=("%y-%m-%d"),
            attrs={"type": "date"}
        ),
        help_text="Date of original livestream",
        required=False
    )
    timestamp = Manual_Field(
        label="Timestamp(s)",
        widget=Tagged_Text_Widget(),
        required=False,
        help_text="Separate with commas. Match order in associated ZFiles.",
    )
    ad_break_endings = Manual_Field(
        label="Ad Break End Timestamp(s)",
        widget=Tagged_Text_Widget(),
        required=False,
        help_text="Timestamps for when ad breaks ended. Must be manually added to list of streamed worlds",
    )

    def refresh_choices(self):
        valid_choices = associated_file_choices()
        self.fields["associated"].choices = valid_choices
        self.fields["associated"].widget.choices = valid_choices


class Prep_Publication_Pack_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Generate Publication Pack"
    publish_date = forms.CharField(
        widget=Enhanced_Date_Widget(buttons=["today", "clear"], clear_label="Clear")
    )
    associated = forms.MultipleChoiceField(
        widget=Ordered_Scrolling_Radio_Widget(choices=associated_file_choices(query="unpublished")),
        choices=associated_file_choices(query="unpublished"),
        label="Associated ZFiles",
        help_text="Select one or more ZFiles",
        required=False,
    )
    prefix = Manual_Field(
        label="Prefix(es)",
        widget=Tagged_Text_Widget(),
        required=False,
        help_text="Separate with commas. Match order in associated ZFiles.",
    )


class Change_Username_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Username"
    heading = "Change Username"
    attrs = {"method": "POST"}
    text_prefix = "<p>You may use this form to change your username. Afterwards, you will be required to login again with your new username and password.</p>"

    current_password = forms.CharField(
        widget=forms.PasswordInput()
    )
    new_username = forms.CharField()
    confirm_username = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        new_username = cleaned_data.get("new_username", "")

        # Check requested username and confirmation match
        if new_username != cleaned_data.get("confirm_username", ""):
            self.add_error("confirm_username", "Username confirmation must match newly requested username")

        # Check prohibited characters
        if "/" in new_username:
            self.add_error("new_username", "Usernames may not contain slashes")

        # Check availability
        if User.objects.filter(username__iexact=new_username).exists():
            self.add_error("new_username", "Requested username is unavailable")

        # Check password
        if not check_password(cleaned_data.get("current_password"), self.db_password):
            self.add_error("current_password", "Invalid password")


class Change_Ascii_Char_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change ASCII Character"
    heading = "Change ASCII Character"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Choose an ASCII representation for yourself. This character will be displayed alongside your username whenever it is used throughout the site.</p>"
    )
    COLOR_CHOICES = (
        ("black", "Black"),
        ("blue", "Blue"),
        ("green", "Green"),
        ("cyan", "Cyan"),
        ("red", "Red"),
        ("purple", "Purple"),
        ("yellow", "Yellow"),
        ("white", "White"),
        ("darkgray", "Dark Gray"),
        ("darkblue", "Dark Blue"),
        ("darkgreen", "Dark Green"),
        ("darkcyan", "Dark Cyan"),
        ("darkred", "Dark Red"),
        ("darkpurple", "Dark Purple"),
        ("darkyellow", "Dark Yellow"),
        ("gray", "Gray")
    )

    character = forms.IntegerField(
        min_value=0,
        max_value=255,
        widget=Ascii_Character_Widget(),
        help_text="Click on an ASCII character in the table to select it",
    )
    foreground = forms.ChoiceField(
        choices=COLOR_CHOICES,
        widget=Ascii_Color_Widget(choices=COLOR_CHOICES),
    )
    background = forms.ChoiceField(
        choices=COLOR_CHOICES,
        widget=Ascii_Color_Widget(choices=COLOR_CHOICES, allow_transparent=True),
    )
    preview = Faux_Field(
        label="Preview",
        widget=Faux_Widget("museum_site/widgets/ascii-preview-widget.html"),
        required=False,
    )


class Change_Pronouns_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Pronouns"
    heading = "Change Pronouns"
    attrs = {"method": "POST"}
    text_prefix = "<p>Select your pronouns so that other can know how to refer to you.</p>"

    PRONOUN_CHOICES = (
        ("N/A", "Prefer not to say"),
        ("He/Him", "He/Him"),
        ("It/Its", "It/Its"),
        ("She/Her", "She/Her"),
        ("They/Them", "They/Them"),
        ("CUSTOM", "Custom (specify below)")
    )

    pronouns = forms.ChoiceField(
        choices=PRONOUN_CHOICES,
        widget=forms.RadioSelect(choices=PRONOUN_CHOICES)
    )
    custom = forms.CharField(required=False)


class Change_Password_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Password"
    heading = "Change Password"
    attrs = {"method": "POST"}
    text_prefix = "<p>You may change your password here. Upon successfully changing your password, you will be required to login again.</p>"

    current_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(min_length=8, widget=forms.PasswordInput(), help_text=PASSWORD_HELP_TEXT)
    confirm_password = forms.CharField(min_length=8, widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password", "")

        # Check requested password and confirmation match
        if new_password != cleaned_data.get("confirm_password", ""):
            self.add_error("confirm_password", "Password confirmation must match newly requested password")

        # Check current password
        if not check_password(cleaned_data.get("current_password"), self.db_password):
            self.add_error("current_password", "Invalid password")


class Change_Email_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Email Address"
    heading = "Change Email Address"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>You may change your account's email address here. This address will be used to help you recover your account in the event your forget your "
        "username or password, so keep it up to date!</p>")

    current_password = forms.CharField(
        widget=forms.PasswordInput()
    )
    new_email = forms.EmailField()
    confirm_email = forms.EmailField()

    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get("new_email", "")

        # Check requested email and confirmation match
        if new_email != cleaned_data.get("confirm_email", ""):
            self.add_error("confirm_email", "Email confirmation must match newly provided email address")

        # Check availability
        if User.objects.filter(email=new_email).exists():
            self.add_error("new_email", "Requested email address is unavailable.")

        # Check current password
        if not check_password(cleaned_data.get("current_password"), self.db_password):
            self.add_error("current_password", "Invalid password")


class Change_Patron_Email_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Patron Email Address"
    heading = "Change Patron Email Address"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>In order for your Museum account to be recognized as a Worlds of ZZT patron, your email address must match with an active patron account. "
        "By default, the email address you signed up for your Museum of ZZT account with is used. If this is not the same email address as your Patreon "
        "email address, you may specify the correct email address here.</p>"
    )

    patron_email = forms.EmailField()


class Change_Patronage_Visibility_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Patronage Visibility"
    heading = "Change Patronage Visibility"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Choose whether or not to disclose your status as a Worlds of ZZT patron on your public profile.</p>"
        "<p>This option has no effect for non-patrons.</p>"
    )

    visibility = forms.ChoiceField(
        widget=forms.RadioSelect(
            choices=(("show", "Show patron status"), ("hide", "Hide patron status"))
        ),
        choices=(("show", "Show patron status"), ("hide", "Hide patron status")),
        label="Patronage Visibility"
    )


class Change_Crediting_Preferences_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Crediting Preferences"
    heading = "Change Crediting Preferences"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Choose how you wish to be credited on the Museum of ZZT's <a href='/credits' target='_blank'>Site Credits</a> page as well as on "
        "Worlds of ZZT <a href='/article/category/livestream/' target='_blank'>Livestreams</a>.</p>"
        "<p>If you would prefer to remain anonymous, leave these fields blank.</p>"
    )

    site_credits_name = forms.CharField(required=False)
    stream_credits_name = forms.CharField(required=False)


class Change_Patron_Stream_Poll_Nominations_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Stream Poll Nominations"
    heading = "Change Stream Poll Nominations"
    attrs = {"method": "POST"}

    stream_poll_nominations = forms.CharField(
        widget=forms.Textarea(),
        label="Nominations",
        help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS)
    )


class Change_Patron_Stream_Selections_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Stream Selections"
    heading = "Change Stream Selections"
    attrs = {"method": "POST"}

    stream_selections = forms.CharField(
        widget=forms.Textarea(),
        label="Stream Selections",
        help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS)
    )


class Change_Closer_Look_Poll_Nominations_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Closer Look Poll Nominations"
    heading = "Change Closer Look Poll Nominations"
    attrs = {"method": "POST"}

    closer_look_nominations = forms.CharField(
        widget=forms.Textarea(),
        label="Closer Look Poll Nominations",
        help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS)
    )


class Change_Guest_Stream_Selections_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Guest Stream Selections"
    heading = "Change Guest Stream Selections"
    attrs = {"method": "POST"}

    guest_stream_selections = forms.CharField(
        widget=forms.Textarea(),
        label="Guest Stream Selections",
        help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS)
    )


class Change_Closer_Look_Selections_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Closer Look Selections"
    heading = "Change Closer Look Selections"
    attrs = {"method": "POST"}

    closer_look_selections = forms.CharField(
        widget=forms.Textarea(),
        label="Closer Look Selections",
        help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS)
    )


class Change_Bkzzt_Topics_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change BKZZT Topics"
    heading = "Change BKZZT Topics"
    attrs = {"method": "POST"}

    bkzzt_topics = forms.CharField(
        widget=forms.Textarea(),
        label="BKZZT Topic Selections",
        help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS)
    )


class User_Registration_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Register Account"
    heading = "Register Account"
    attrs = {"method": "POST"}

    requested_username = forms.CharField(label="Username")
    requested_email = forms.EmailField(label="Email address", help_text="A valid email address is required to verify your account.")
    action = forms.CharField(widget=forms.HiddenInput(), initial="register")
    first_name = forms.CharField(required=False)  # Spam trap
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(),
        help_text=PASSWORD_HELP_TEXT
    )
    confirm_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(),
    )
    terms = forms.BooleanField(
        widget=Terms_Of_Service_Widget(terms=TERMS)
    )

    def clean(self):
        cleaned_data = super().clean()

        # Check if username is taken
        if User.objects.filter(username__iexact=cleaned_data.get("requested_username")).exists():
            self.add_error("requested_username", "Requested username is unavailable")

        # Check if email is taken
        if User.objects.filter(email=cleaned_data.get("requested_email")).exists():
            self.add_error("requested_email", "Requested email address is unavailable.")

        # Check passwords match
        if cleaned_data.get("password", "") != cleaned_data.get("confirm_password", ""):
            self.add_error("confirm_password", "Password confirmation must match password")

        # Adjust TOS error message
        if not cleaned_data.get("terms"):
            self.add_error("terms", "You must agree to the terms of service in order to register an account.")

        return cleaned_data


class Activate_Account_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Activate Account"
    heading = "Activate Account"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Your account has been created, but is currently <b>INACTIVE</b>.</p>"
        "<p>Please wait a moment and then check your inbox for an email containing a link to verify your account. "
        "If you haven't received one, check your spam folder as well. "
        "If you still haven't received a verification message <a href='mailto:{}'> contact Dr. Dos</a> for manual activation.</p>"
        "<p><a href='/user/resend-activation'>Resend activation email</a>.</p>".format(EMAIL_ADDRESS)
    )

    activation_token = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()

        qs = User.objects.filter(profile__activation_token=cleaned_data.get("activation_token"))

        if len(qs) != 1:
            self.add_error("activation_token", "A user account with the provided token was not found")
        else:
            cleaned_data["user"] = qs.first()
        return cleaned_data


class Forgot_Username_Form(forms.Form):
    use_required_attribute = False
    heading = "Forgot Username"
    submit_value = "Find Username"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Please provide the email address for your account. If an account with that email address exists, "
        "a message will be sent to that address providing your username.</p>"
    )

    email = forms.EmailField(label="Account email address")


class Forgot_Password_Form(forms.Form):
    use_required_attribute = False
    heading = "Forgot Password"
    submit_value = "Request Password Reset"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Please provide the email address for your account. If an account with that email address exists, "
        "a message will be sent to that address containing a link to reset your password.</p>"
    )

    email = forms.EmailField(label="Account email address")


class Reset_Password_Form(forms.Form):
    use_required_attribute = False
    heading = "Reset Password"
    submit_value = "Change Password"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>Your request has been received. If the provided email has an associated account, an email will be sent to containing a token to reset "
        "your password. A link is also provided to automatically enter the token's value. This token will expire in 10 minutes.</p>"
        "<p>If no message is received, check your spam folder and wait a few minutes before trying again. If the issue persists, contact "
        "<a href='mailto:{}'>Dr. Dos</a>.</p>".format(EMAIL_ADDRESS)
    )

    reset_token = forms.CharField()
    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(),
        help_text=PASSWORD_HELP_TEXT
    )
    confirm_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput()
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password", "")

        # Check requested password and confirmation match
        if new_password != cleaned_data.get("confirm_password", ""):
            self.add_error("confirm_password", "Password confirmation must match newly requested password")

        # Check the token is valid
        qs = User.objects.filter(profile__reset_token=cleaned_data.get("reset_token"))

        if len(qs) != 1:
            self.add_error("reset_token", "The provided reset token is either invalid or expired.")
        else:
            delta = qs[0].profile.reset_time + timedelta(minutes=10)
            if datetime.now(timezone.utc) > delta:
                self.add_error("reset_token", "The provided reset token is either invalid or expired.")
            else:
                self.user = qs[0]
        return cleaned_data


class Resent_Account_Activation_Email_Form(forms.Form):
    use_required_attribute = False
    heading = "Resend Account Activation Email"
    submit_value = "Resend Activation Email"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>If you haven't received your account activation email or your activation token has expired you can provide your email address here "
        "to have another one sent to your account.</p>"
        "<p>If you continue to not receive an activation email, contact "
        "<a href='mailto:{}'>Dr. Dos</a> for manual account activation..</p>".format(EMAIL_ADDRESS)
    )

    email = forms.EmailField()


class Updated_Terms_Of_Service_Form(forms.Form):
    use_required_attribute = False
    heading = "Updated Terms of Service"
    submit_value = "Accept Terms of Service"
    attrs = {"method": "POST"}
    text_prefix = (
        "<p>The Museum of ZZT's terms of service have been updated since you last agreed to the terms. In order to continue using your account you "
        "must accept the current version of the terms.</p>"
    )

    terms = forms.BooleanField(
        widget=Terms_Of_Service_Widget(terms=TERMS)
    )

    def clean(self):
        cleaned_data = super().clean()

        # Adjust TOS error message
        if not cleaned_data.get("terms"):
            self.add_error("terms", "You must agree to the terms of service in order to register an account.")
        return cleaned_data


class Login_Form(forms.Form):
    use_required_attribute = False
    heading = "Account Login"
    submit_value = "Login"
    attrs = {"method": "POST"}

    action = forms.CharField(widget=forms.HiddenInput(), initial="login")
    username = forms.CharField(
        help_text="<a href='/user/forgot-username/' tabindex='-1'>Forgot Username</a>"
    )
    password = forms.CharField(
        help_text="<a href='/user/forgot-password/' tabindex='-1'>Forgot Password</a>",
        widget=forms.PasswordInput()
    )


class Tool_ZFile_Select_Form(forms.Form):
    use_required_attribute = False

    key = forms.ChoiceField(
        label="ZFile",
        choices=qs_to_select_choices(File.objects.all().only("id", "title", "key"), val="{0.key}"),
    )


class Stream_Card_Form(forms.Form):
    use_required_attribute = False

    pk = forms.MultipleChoiceField(
        widget=Ordered_Scrolling_Radio_Widget(choices=associated_file_choices()),
        choices=associated_file_choices(),
        label="Associated ZFiles",
        help_text="Select one or more ZFiles",
        required=False,
    )


class Livestream_Vod_Form(forms.Form):
    use_required_attribute = False
    heading = "Add Livestream VOD"
    submit_value = "Add Livestream VOD"
    attrs = {"method": "POST", "enctype": "multipart/form-data"}

    author = forms.CharField(initial="Dr. Dos")
    title = forms.CharField(widget=Enhanced_Text_Widget(char_limit=80), help_text="Used exactly as entered. Don't forget the 'Livestream - ' prefix!")
    date = forms.DateField(widget=Enhanced_Date_Widget(buttons=["today"]))
    video_url = forms.URLField(help_text=(
            "https://youtu.be/<b>{id}</b>, <br>https://www.youtube.com/watch?v=<b>{id}</b>&feature=youtu.be, <br>"
            "or https://studio.youtube.com/video/<b>{id}</b>/edit format."
        ),
        label="Video URL"
    )
    video_description = forms.CharField(
        widget=forms.Textarea(),
        help_text=(
            "Copy/Paste from YouTube video details editor. Manually erase everything from "
            "'<i>Join us for future livestreams...</i>' to the end of the description."
        )
    )
    description = forms.CharField(widget=Enhanced_Text_Widget(char_limit=250), label="Article Summary")
    preview_image = forms.FileField()
    crop = forms.ChoiceField(label="Preview Image Crop", choices=PREVIEW_IMAGE_CROP_CHOICES)
    publication_status = forms.ChoiceField(choices=Article.PUBLICATION_STATES)
    series = forms.ChoiceField(choices=qs_to_select_choices(Series.objects.filter(visible=True), allow_none=True))
    associated_zfile = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(
            choices=associated_file_choices,
            filterable=True,
            show_selected=True,
        ),
        choices=associated_file_choices,
        required=False,
    )

    def clean_video_url(self):
        video_url = self.cleaned_data["video_url"]

        # Strip the URL part and get the ID
        video_url = video_url.replace("https://youtu.be/", "")
        video_url = video_url.replace("https://www.youtube.com/watch?v=", "")
        video_url = video_url.replace("https://studio.youtube.com/video/", "")
        video_url = video_url.replace("/edit", "")
        if "&" in video_url:
            video_url = video_url[:video_url.find("&")]

        return video_url

    def create_article(self):
        preview_image = self.files["preview_image"]

        # Prepare the Article
        a = Article()
        key = ("pk-" + self.cleaned_data["associated_zfile"][0]) if self.cleaned_data["associated_zfile"] else "no-assoc"
        a.title = self.cleaned_data["title"]
        a.author = self.cleaned_data["author"]
        a.category = "Livestream"
        a.schema = "django"
        a.publish_date = self.cleaned_data["date"]
        a.published = self.cleaned_data["publication_status"]
        a.description = self.cleaned_data["description"]
        a.static_directory = "ls-{}-{}".format(key, self.cleaned_data["video_url"])
        a.allow_comments = True

        # Context for subtemplate
        final_desc = urlize(self.cleaned_data["video_description"])
        final_desc = linebreaks(final_desc)
        subcontext = {"video_id": self.cleaned_data["video_url"], "desc": final_desc}

        # Render the subtemplate
        a.content = render_to_string("museum_site/subtemplate/stream-vod-article.html", subcontext)

        # Process the uploaded image
        folder = os.path.join(SITE_ROOT, "museum_site", "static", "articles", str(self.cleaned_data["date"])[:4], a.static_directory)
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass

        # Save the file to the uploaded folder
        file_path = os.path.join(folder, "preview.png")
        with open(file_path, 'wb+') as fh:
            for chunk in preview_image.chunks():
                fh.write(chunk)

        # Crop image if needed
        if self.cleaned_data.get("crop") != "NONE":
            crop_file(file_path, preset=self.cleaned_data["crop"])

        # Save the article so it has an ID
        a.save()

        # Associate the article with the relevant file(s)
        for file_association in self.cleaned_data["associated_zfile"]:
            fa = File.objects.get(pk=int(file_association))
            fa.articles.add(a)
            fa.save()

        # Associate the article with the selected series (if any)
        if self.cleaned_data["series"] != "none":
            series = Series.objects.get(pk=int(self.cleaned_data["series"]))
            a.series.add(series)
            a.save()

        return a


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


""" ON HITATUS
class Tinyzoo_Converter_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Convert ZZT File"
    attrs = {"method": "POST"}

    zfile = forms.FileField(
        help_text=("Select the file you wish to convert. File must be in .ZZT format."),
        label="Input file", widget=UploadFileWidget(target_text="Drag & Drop a ZZT File Here or Click to Choose", allowed_filetypes=".zzt")
    )
    output_filename = forms.CharField(
        label="Custom output filename:", help_text="Manually specified filename for the converted file. Leave blank for &lt;world&gt;.gbc"
    )
    engine = forms.ChoiceField(
        choices=(
            ("gbx", "Game Boy (Color)"),
            ("ap", "Analogue Pocket"),
        )
    )
"""
