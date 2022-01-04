import glob
import os
import shutil
import time
import zipfile

from django import forms
from .models import File, Upload, Zeta_Config, Download, Detail
from .fields import *
from .widgets import *
from .common import GENRE_LIST, YEAR, any_plus, TEMP_PATH, SITE_ROOT
from .constants import LICENSE_CHOICES, LICENSE_SOURCE_CHOICES, LANGUAGE_CHOICES, DETAIL_REMOVED
from .private import IA_ACCESS, IA_SECRET


from internetarchive import upload



class ZGameForm(forms.ModelForm):
    zfile = forms.FileField(
        help_text=("Select the file you wish to upload. "
                   "All uploads <i>must</i> be zipped."),
        label="File", widget=UploadFileWidget()
    )

    use_required_attribute = False
    # Properties handled in view
    max_upload_size = 0
    editing = False
    expected_file_id = 0  # For replacing a zip

    class Meta:
        model = File

        fields = [
            "zfile", "title", "author", "company", "genre", "explicit",
            "release_date", "language",
            "description",
        ]

        help_texts = {
            "title": "Leave A/An/The as the first word if applicable.",
            "author": (
                "Separate multiple authors with a comma. Do not abbreviate "
                "names.<br>"
                "For files with many authors, consider using the compiler as "
                "the author with \"Various\" to represent the rest. Try to "
                "sort multiple authors from most to least important on this "
                "particular upload."
            ),
            "company": (
                "Any companies this file is published under. If there are "
                "none, leave this field blank. If there are multiple, "
                "separate them with a comma."
            ),
            "genre": (
                "Check any applicable genres that describe the content of the "
                "uploaded file. Use 'Other' if a genre isn't represented and "
                "mention it in the upload notes field in the Upload Settings "
                "section."
            ),
            "release_date": (
                "Enter the date this file was first made public. If this is a "
                "new release, it should be the modified date of the most "
                "recent ZZT world (or executable, or other primary file). If "
                "the release date is not known, leave this field blank."
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
                "An optional description of the upload. For utilities, please "
                "be sure to fill this out."
            ),
            "explicit": (
                "Check this box if the upload contains material not suitable "
                "for minors or non-consenting adults. Uploads marked as "
                "explicit will require confirmation before accessing and "
                "never appear in Worlds of ZZT bot posts."
            ),
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
            "Xedit_token": forms.HiddenInput(),
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
    board_min = forms.IntegerField(required=False, label="Minimum/Maximum board count")
    board_max = forms.IntegerField(required=False)
    board_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices =[
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
        #widget=forms.SelectMultiple,
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

    def clean(self):
        language = self.data["language"]

        print("SELF.DATA", self.data)

        print("Ok?", language)
        return language


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
        ("czoo420b3-dos.zip", "ClassicZoo v4.20 beta 3::ZZT.EXE"),
        ("sczo404.zip", "Super ClassicZoo v4.04::SUPERZ.EXE"),
    )

    title = forms.CharField(label="Title")
    url = forms.CharField(label="Url", help_text="")
    creator = forms.CharField(label="Creator")
    year = forms.IntegerField(label="Year")
    subject = forms.CharField(label="Subject", help_text="Separate with commas")
    description = forms.CharField(label="Description", widget=forms.Textarea(), help_text="Can contain links, formatting and images in html/css")
    collection = forms.ChoiceField(choices=COLLECTIONS)
    language = forms.ChoiceField(choices=IA_LANGUAGES, initial="eng")
    alternate_zfile = forms.FileField(
        required=False,
        help_text=("Alternative zipfile to use instead of the Museum's copy"),
        label="Alternate Zip",
        widget=UploadFileWidget()
    )
    packages = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=PACKAGES, help_text="Additional zipfiles whose contents are to be included")
    default_world = forms.ChoiceField(choices=[])
    launch_command = forms.CharField(required=False)

    def mirror(self, zfile):
        archive_title = self.cleaned_data["title"]
        # Copy the file's zip into a temp directory
        if self.cleaned_data["collection"] == "test_collection":
            ts = str(int(time.time()))
            wip_zf_name = "test_" + ts + "_" + self.cleaned_data["url"]
            archive_title = "Test - " + ts + "_" + archive_title
        else:
            wip_zf_name = self.cleaned_data["url"]

        wip_dir = os.path.join(TEMP_PATH, os.path.splitext(wip_zf_name)[0])
        wip_zf_path = os.path.join(wip_dir, wip_zf_name)
        try:
            os.mkdir(wip_dir)
        except FileExistsError:
            pass

        # Extract zfile
        zf = zipfile.ZipFile(zfile.phys_path())
        files = zf.infolist()
        comment = zf.comment
        for f in files:
            print(f.filename, f.date_time)
            zf.extract(f, path=wip_dir)
            timestamp = time.mktime(f.date_time + (0, 0, -1))
            os.utime(os.path.join(wip_dir, f.filename), (timestamp, timestamp))
        zf.close()

        # Extract any additional packages
        for package in self.cleaned_data["packages"]:
            package_path = os.path.join(SITE_ROOT, "museum_site", "static", "data", "ia_packages", package)
            zf = zipfile.ZipFile(package_path)
            files = zf.infolist()
            for f in files:
                print(f.filename, f.date_time)
                zf.extract(f, path=wip_dir)
                timestamp = time.mktime(f.date_time + (0, 0, -1))
                os.utime(os.path.join(wip_dir, f.filename), (timestamp, timestamp))
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
            "year": str(self.cleaned_data["year"]),
            "subject": self.cleaned_data["subject"],
            "creator": self.cleaned_data["creator"],
            "description": self.cleaned_data["description"]
        }

        # Mirror the file
        print("HERE I GO!")
        print("Name", wip_zf_name)
        print("Path", wip_zf_path)

        r = upload(
            wip_zf_name,
            files=[wip_zf_path],
            metadata=meta,
            access_key=IA_ACCESS,
            secret_key=IA_SECRET,
        )
        print(r)

        print("Okay...")

        print("MIRRORED?")
