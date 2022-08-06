import glob
import os
import shutil
import time
import zipfile

from datetime import datetime

from django import forms
from django.urls import reverse_lazy
from museum_site.core import *
from museum_site.models import *
from museum_site.fields import *
from museum_site.widgets import *
from museum_site.common import GENRE_LIST, YEAR, any_plus, TEMP_PATH, SITE_ROOT, get_sort_option_form_choices, delete_this, UPLOAD_TEST_MODE, record
from museum_site.constants import (
    LICENSE_CHOICES, LICENSE_SOURCE_CHOICES, LANGUAGE_CHOICES
)
from museum_site.core.detail_identifiers import *
from museum_site.private import IA_ACCESS, IA_SECRET


from internetarchive import upload

STUB_CHOICES = (("A", "First"), ("B", "Second"), ("C", "Third"))  # For debugging


class ZGameForm(forms.ModelForm):
    field_order = ["zfile", "title", "author", "company", "genre", "explicit", "release_date", "language", "description"]
    zfile = forms.FileField(
        help_text=("Select the file you wish to upload. "
                   "All uploads <i>must</i> be zipped."),
        label="File", widget=UploadFileWidget()
    )
    genre = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(
            choices=qs_to_categorized_select_choices(
                Detail.objects.filter(visible=True),
            ),
            buttons=["Clear"],
            show_selected=True,
        ),
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

        fields = [
            "zfile", "title", "author", "company", "explicit",
            "release_date",
            "description",
        ]

        help_texts = {
            "title": "Leave A/An/The as the first word if applicable.",
            "company": (
                "Any companies this file is published under. If there are "
                "none, leave this field blank. If there are multiple, "
                "separate them with a comma."
            ),
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
            "file_license": "The license under which this world is published.",
            "license_source": (
                "Where the license can be found. Use a source contained "
                "within the uploaded file when possible."
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
            "company": Tagged_Text_Widget(),
            "explicit": forms.RadioSelect(
                choices=(
                    (0, "This upload does not contain explicit content"),
                    (1, "This upload contains explicit content")
                ),
            ),
            "release_date": Enhanced_Date_Widget(buttons=["today", "clear"], clear_label="Unknown"),
            "file_license": SelectPlusCustomWidget(
                choices=LICENSE_CHOICES
            ),
            "license_source": SelectPlusCustomWidget(
                choices=LICENSE_SOURCE_CHOICES
            ),
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
        author = self.cleaned_data["author"].replace("[text]", "")
        author = author.replace(",", "/")

        if author.endswith("/"):
            author = author[:-1]

        # Replace blank authors with "Unknown"
        if author == "":
            author = "Unknown"
        return author

    def clean_company(self):
        company = self.cleaned_data["company"].replace("[text]", "")
        company = company.replace(",", "/")

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
        label="Minimum/Maximum board count",
        widget=Board_Range_Widget(min_val=0, max_val=999, max_length=3),
        required=False,
    )
    year = forms.ChoiceField(
        label="Release year",
        choices=range_select_choices(1991, YEAR, allow_any=True, allow_unknown=True, order="desc"),
        required=False,
    )
    rating = Manual_Field(
        label="Minimum/Maximum rating",
        widget=Range_Widget(min_val=0, max_val=5, max_length=4, step=0.1),
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
            default=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_WEAVE]
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
            requested_min = int(requested_min)
            requested_max = int(requested_max)

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
        r = upload(
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
        (-1, "No rating"),
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
    associations = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={"class": "ul-scrolling-checklist"}),
        choices=list(Article.objects.not_removed().values_list("id", "title")),
        required=False,
        label="Associated Files"
    )
    preview = forms.FileField(
        label="Preview Image",
        help_text="Cropped to 480x350"
    )

    class Meta:
        model = Series
        fields = ["title", "description", "visible"]


def associated_file_choices():
    raw = File.objects.only("id", "title", "key")
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


class Debug_Form(forms.Form):
    use_required_attribute = False
    manual_fields = ["board", "associated", "ssv_author", "ssv_company", "rating"]

    file_radio = forms.ChoiceField(
        widget=Scrolling_Radio_Widget(choices=associated_file_choices()),
        choices=associated_file_choices(),
        label="File Select Radio Widget",
        help_text="Selecting one file as radio buttons",
        required=False,
    )
    file_check = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(choices=associated_file_choices()),
        choices=associated_file_choices(),
        label="File Select Checkbox Widget",
        help_text="Selecting many files via checkboxes",
        required=False,
    )
    limited_text = forms.CharField(
        widget=Enhanced_Text_Widget(char_limit=69),
        label="Limited Text Field",
        help_text="You get 69 characters. Nice.",
        required=False,
    )
    date_with_buttons = forms.DateField(
        widget=Enhanced_Date_Widget(buttons=["today", "clear"], clear_label="Unknown"),
        label="Date Field With Buttons",
        help_text="Today and Unknown",
        required=False,
    )
    genre = forms.ChoiceField(
        choices=qs_to_select_choices(Genre.objects.filter(visible=True).only("pk", "title", "slug"), allow_any=True, val="{0.title}"),
        required=False,
    )
    board = Manual_Field(
        widget=Board_Range_Widget(min_val=0, max_val=999, max_length=3),
        required=False,
    )
    associated = Manual_Field(
        label="Related Content",
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
            default=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_WEAVE]
        ),
        choices=qs_to_categorized_select_choices(Detail.objects.filter(visible=True), category_order=["ZZT", "SZZT", "Media", "Other"]),
        required=False,
    )
    nonfilterable = forms.MultipleChoiceField(
        widget=Scrolling_Checklist_Widget(
            choices=(("A", "A"), ("B", "B"), ("C", "C")),
            filterable=False,
            buttons=["All", "Clear", "Default"],
            show_selected=True,
            default=["A", "C"]
        ),
        choices=(("A", "A"), ("B", "B"), ("C", "C")),
        required=False,
    )
    ssv_author = Manual_Field(
        label="Author(s)",
        widget=Tagged_Text_Widget(),
        required=False,
    )
    ssv_company = Manual_Field(
        label="Company",
        widget=Tagged_Text_Widget(suggestions=Genre.objects.all().values_list("title", flat=True)),
        required=False,
    )
    rating = Manual_Field(
        label="Rating range",
        widget=Range_Widget(min_val=0, max_val=5, max_length=4, step=0.1),
        required=False,
    )

    def __init__(self, data=None):
        super().__init__(data)
        # Handle Manual Fields
        for field in self.manual_fields:
            self.fields[field].widget.manual_data = self.data.copy()  # Copy to make mutable
            # Coerce specific min/max inputs to generic min/max keys
            self.fields[field].widget.manual_data["min"] = self.fields[field].widget.manual_data.get(field + "_min")
            self.fields[field].widget.manual_data["max"] = self.fields[field].widget.manual_data.get(field + "_max")
            # Tags need to be joined as a string
            if data and isinstance(self.fields[field].widget, Tagged_Text_Widget):
                raw = self.data.getlist(field)
                if raw[0] == "[text]":  # Matched our template for JS
                    raw = raw[1:]
                joined = ",".join(raw) + ","
                if len(joined) > 1:
                    self.fields[field].widget.manual_data["tags_as_string"] = joined


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


class Prep_Publication_Pack_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Generate Publication Pack"
    publish_date = forms.CharField(
        widget=Enhanced_Date_Widget(buttons=["today", "clear"], clear_label="Clear")
    )
    associated = forms.MultipleChoiceField(
        widget=Ordered_Scrolling_Radio_Widget(choices=associated_file_choices()),
        choices=associated_file_choices(),
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
