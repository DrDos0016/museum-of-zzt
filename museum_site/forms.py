import glob
import os
import shutil
import time
import zipfile

from django import forms
from museum_site.models import *
from museum_site.fields import *
from museum_site.widgets import *
from museum_site.common import GENRE_LIST, YEAR, any_plus, TEMP_PATH, SITE_ROOT
from museum_site.constants import (
    LICENSE_CHOICES, LICENSE_SOURCE_CHOICES, LANGUAGE_CHOICES, DETAIL_REMOVED
)
from museum_site.private import IA_ACCESS, IA_SECRET


from internetarchive import upload


class ZGameForm(forms.ModelForm):
    zfile = forms.FileField(
        help_text=("Select the file you wish to upload. "
                   "All uploads <i>must</i> be zipped."),
        label="File", widget=UploadFileWidget()
    )
    genres = forms.CharField(
        help_text=(
            "Check any applicable genres that describe the content of the "
            "uploaded file. Use 'Other' if a genre isn't represented and "
            "mention it in the upload notes field in the Upload Settings "
            "section. For a description of genres, see the "
            "<a href='/help/genre/' target='_blank'>Genre Overview</a> "
            "page."
        ),
        widget=SlashSeparatedValueCheckboxWidget(
            choices=list(
                zip(
                    Genre.objects.filter(visible=True), Genre.objects.filter(
                        visible=True
                    )
                )
            )
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
        widget=SlashSeparatedValueWidget(
            attrs={
                "list": "author-suggestions",
                "autocomplete": "off",
            }
        )
    )

    field_order = ["zfile", "title", "author", "company", "genres"]

    use_required_attribute = False
    # Properties handled in view
    max_upload_size = 0
    editing = False
    expected_file_id = 0  # For replacing a zip

    class Meta:
        model = File

        fields = [
            "zfile", "title", "author", "company", "explicit",
            "release_date", "language",
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
            "language": (
                'Check any languages the player is expected to understand to '
                'comprehend the files in the upload. For worlds exclusively '
                'using created languages, use "Other". If a language is not '
                'listed, use "Other" and specify the correct language in the '
                'upload notes section.'
            ),
            "license": "The license under which this world is published.",
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
            "company": SlashSeparatedValueWidget(
                attrs={
                    "list": "company-suggestions",
                    "autocomplete": "off",
                    }
            ),
            "explicit": forms.RadioSelect(
                choices=(
                    (0, "This upload does not contain explicit content"),
                    (1, "This upload contains explicit content")
                ),
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

        if zfile and zfile.name:
            dupe = File.objects.filter(filename=zfile.name).first()
            if dupe and dupe.id != self.expected_file_id:
                raise forms.ValidationError(
                    "The selected filename is already in use. "
                    "Please rename your zipfile."
                )

        if zfile and zfile.size > self.max_upload_size:
            raise forms.ValidationError(
                "File exceeds your maximum upload size! "
                "Contact Dr. Dos for a manual upload."
            )

    def clean_author(self):
        # Replace blank authors with "Unknown"
        author = self.cleaned_data["author"]

        if author == "":
            author = "Unknown"
        return author

    def clean_genres(self):
        # Make sure all requested genres exist
        valid_genres = list(Genre.objects.filter(visible=True).values_list("title", flat=True))

        requested_genres = self.cleaned_data["genres"].split("/")

        for genre in requested_genres:
            if genre not in valid_genres:
                raise forms.ValidationError(
                    "An invalid genre was specified."
                )


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


class AdvancedSearchForm(forms.Form):
    use_required_attribute = False
    required = False

    title = forms.CharField(label="Title contains", required=False)
    author = forms.CharField(label="Author contains", required=False)
    filename = forms.CharField(label="Filename contains", required=False)
    company = forms.CharField(label="Company contains", required=False)
    genre = forms.ChoiceField(
        choices=any_plus(zip(GENRE_LIST, GENRE_LIST)),
        required=False
    )
    year = forms.ChoiceField(
        choices=any_plus(((str(x), str(x)) for x in range(1991, YEAR + 1))),
        required=False
    )
    board_min = forms.IntegerField(
        required=False, label="Minimum/Maximum board count"
    )
    board_max = forms.IntegerField(required=False)
    board_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[
            ("playable", "Playable Boards"),
            ("total", "Total Boards"),
        ],
        required=False,
        )

    language = forms.ChoiceField(
        choices=any_plus(LANGUAGE_CHOICES),
        required=False,
    )
    reviews = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=(
            ("yes", "Show files with reviews"),
            ("no", "Show files without reviews"),
            ("any", "Show both")
        ),
        required=False,
    )
    articles = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=(
            ("yes", "Show files with articles"),
            ("no", "Show files without articles"),
            ("any", "Show both")
        ),
        required=False
    )
    details = forms.MultipleChoiceField(
        # widget=forms.SelectMultiple,
        widget=GroupedCheckboxWidget,
        choices=Detail.objects.form_list,
        required=False,
    )
    sort = forms.ChoiceField(
        label="Sort by",
        choices=(
            ("title", "Title"),
            ("author", "Author"),
            ("company", "Company"),
            ("rating", "Rating"),
            ("release", "Release Date"),
        ),
        required=False
    )


class ArticleSearchForm(forms.Form):
    use_required_attribute = False
    required = False

    YEARS = (
        [("Any", "- ANY - ")] +
        [(y, y) for y in range(YEAR, 1990, -1)] +
        [("Unk", "Unknown")]
    )

    # TODO this may need to be moved/replaced if DB model changes
    CATEGORIES = (
        ("Bugs And Glitches", "Bugs And Glitches"),
        ("Closer Look", "Closer Look"),
        ("Contest", "Contest"),
        ("Featured Game", "Featured Game"),
        ("Help", "Help"),
        ("Historical", "Historical"),
        ("Interview", "Interview"),
        ("Let's Play", "Let's Play"),
        ("Livestream", "Livestream"),
        ("Postmortem", "Postmortem"),
        ("Publication Pack", "Publication Pack"),
        ("Walkthrough", "Walkthrough"),
        ("Misc", "Misc.")
    )

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

    title = forms.CharField(label="Title contains")
    author = forms.CharField(label="Author contains")
    text = forms.CharField(label="Text contains")
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
                os.remove(f)
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
