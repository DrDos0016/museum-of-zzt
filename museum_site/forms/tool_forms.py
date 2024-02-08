import base64
import glob
import json
import os
import time
import tempfile
import zipfile

import requests

from django import forms
from django.template.defaultfilters import linebreaks, urlize
from django.template.loader import render_to_string

from internetarchive import upload as ia_upload

from museum_site.core.file_utils import delete_this
from museum_site.core.image_utils import crop_file, optimize_image
from museum_site.core.social import Social_Twitter, Social_Mastodon
from museum_site.constants import APP_ROOT, DATA_PATH, STATIC_PATH
from museum_site.settings import (
    IA_ACCESS, IA_SECRET, DISCORD_WEBHOOK_ANNOUNCEMENTS_URL, DISCORD_WEBHOOK_PATRONS_URL, DISCORD_WEBHOOK_TEST_URL, DISCORD_WEBHOOK_FEED_URL,
)
from museum_site.fields import (
    Enhanced_Model_Choice_Field, Manual_Field, Museum_Drag_And_Drop_File_Field, Museum_Model_Scrolling_Multiple_Choice_Field, Museum_Tagged_Model_Choice_Field,
    Museum_Tagged_Text_Field
)
from museum_site.models import Article, File, Series
from museum_site.widgets import (
    Ascii_Color_Widget,
    Enhanced_Date_Widget, Enhanced_Text_Widget, Ordered_Scrolling_Radio_Widget, Scrolling_Checklist_Widget, Tagged_Text_Widget, UploadFileWidget
)


PREVIEW_IMAGE_CROP_CHOICES = (
    ("ZZT", "480x350 ZZT Board"),
    ("SZZT", "448x400 Super ZZT Board"),
    ("NONE", "Do Not Crop Image"),
)


class Discord_Announcement_Form(forms.Form):
    use_required_attribute = False
    heading = "Discord Announcement"
    attrs = {"method": "POST"}
    submit_value = "Announce"

    CHANNELS = (
        ("announcements", "Announcements"),
        ("patrons", "Patrons"),
        ("moz-feed", "Museum of ZZT Feed"),
        ("test", "Test Announcement (#bot-dev)"),
    )

    channel = forms.ChoiceField(choices=CHANNELS, initial="announcements")
    body = forms.CharField(
        label="Body",
        widget=forms.Textarea(),
        help_text="Discord Markdown supported"
    )

    def process(self):
        destinations = {
            "announcements": DISCORD_WEBHOOK_ANNOUNCEMENTS_URL, "patrons": DISCORD_WEBHOOK_PATRONS_URL, "moz-feed": DISCORD_WEBHOOK_FEED_URL,
            "test": DISCORD_WEBHOOK_TEST_URL
        }
        destination_webhook = destinations.get(self.cleaned_data["channel"])

        discord_data = {"content": self.cleaned_data["body"],}
        resp = requests.post(destination_webhook, headers={"Content-Type": "application/json"}, data=json.dumps(discord_data))
        print(resp)
        self.response = resp


class IA_Mirror_Form(forms.Form):
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
        else:
            wip_zf_name = self.cleaned_data["filename"]
            url = self.cleaned_data["url"]

        temp_dir = tempfile.TemporaryDirectory(prefix="moz-ia")
        wip_dir = temp_dir.name
        wip_zf_path = os.path.join(wip_dir, wip_zf_name)

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
            package_path = os.path.join(DATA_PATH, "ia_packages", package)
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


class Series_Form(forms.ModelForm):
    user_required_attribute = False
    attrs = {"method": "POST", "enctype": "multipart/form-data"}
    submit_value = "Add Series"

    associations = forms.ModelMultipleChoiceField(
        label="Associated Articles",
        required=False,
        queryset=Article.objects.accessible(),
        to_field_name="pk",
        widget=Scrolling_Checklist_Widget(
            buttons=["Clear"],
            show_selected=True,
        )
    )
    preview = Museum_Drag_And_Drop_File_Field(
        help_text="Select the image you wish to upload.",
        label="Preview Image",
        widget=UploadFileWidget(target_text="Drag & Drop A File Here or Click to Choose", allowed_preset="image"),
    )
    crop = forms.ChoiceField(label="Preview Image Crop", choices=PREVIEW_IMAGE_CROP_CHOICES)

    class Meta:
        model = Series
        fields = ["title", "description", "visible"]


class Livestream_Description_Form(forms.Form):
    heading = "Livestream Description Generator"
    use_required_attribute = False
    submit_value = "Select"

    associated = Enhanced_Model_Choice_Field(
        widget=Ordered_Scrolling_Radio_Widget(),
        queryset=File.objects.all(),
        label="Associated ZFiles",
        help_text="Select one or more ZFiles",
        required=False,
        empty_label=None
    )
    stream_date = forms.CharField(
        widget=forms.DateInput(attrs={"type": "date"}),
        help_text="Date of original livestream",
        required=False
    )


    timestamp = Museum_Tagged_Text_Field(
        label="Timestamp(s)",
        required=False,
        help_text="Separate with commas. Match order in associated ZFiles.",
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
            "or https://studio.youtube.com/video/<b>{id}</b>/edit format. Add multiplate with commas (no space)."
        ),
        label="Video URL"
    )
    video_description = forms.CharField(
        widget=forms.Textarea(),
        help_text="Copy/Paste from YouTube video details editor. Everything from '♦ Join...' will be truncated"
    )
    description = forms.CharField(widget=Enhanced_Text_Widget(char_limit=250), label="Article Summary")
    preview_image = forms.FileField()
    crop = forms.ChoiceField(label="Preview Image Crop", choices=PREVIEW_IMAGE_CROP_CHOICES)
    publication_status = forms.ChoiceField(choices=Article.PUBLICATION_STATES)
    series = forms.ModelChoiceField(queryset=Series.objects.visible(), empty_label="- NONE -", required=False)
    associated_zfile = Enhanced_Model_Choice_Field(
        widget=Scrolling_Checklist_Widget(
            filterable=True,
            show_selected=True,
        ),
        queryset=File.objects.all(),
        empty_label=None,
        required=False,
    )

    def clean_video_url(self):
        videos = self.cleaned_data["video_url"].split(",")
        video_urls = []

        for video_url in videos:
            print("OG URL", video_url)
            # Strip the URL part and get the ID
            video_url = video_url.replace("https://youtu.be/", "")
            video_url = video_url.replace("https://www.youtube.com/watch?v=", "")
            video_url = video_url.replace("https://studio.youtube.com/video/", "")
            video_url = video_url.replace("/edit", "")
            if "&" in video_url:
                video_url = video_url[:video_url.find("&")]
            video_urls.append(video_url)

        return video_urls

    def clean_video_description(self):
        video_description = self.cleaned_data["video_description"]
        if "♦ Join" in video_description:
            video_description = video_description[:video_description.find("♦ Join")]
        return video_description

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
        a.static_directory = "ls-{}-{}".format(key, self.cleaned_data["video_url"][0])
        a.allow_comments = True

        # Context for subtemplate
        final_desc = urlize(self.cleaned_data["video_description"])
        final_desc = linebreaks(final_desc)
        subcontext = {"video_ids": self.cleaned_data["video_url"], "desc": final_desc}

        # Render the subtemplate
        a.content = render_to_string("museum_site/subtemplate/stream-vod-article.html", subcontext)

        # Process the uploaded image
        folder = os.path.join(STATIC_PATH, "articles", str(self.cleaned_data["date"])[:4], a.static_directory)
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
            fa.save()  # FULLSAVE

        # Associate the article with the selected series (if any)
        if self.cleaned_data["series"]:
            a.series.add(self.cleaned_data["series"])
            a.save()

        return a


class Prep_Publication_Pack_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Generate Publication Pack"

    associated = Museum_Tagged_Model_Choice_Field(
        widget=Ordered_Scrolling_Radio_Widget(),
        queryset=File.objects.unpublished(),
        label="ZFiles to publish",
        help_text="Select one or more ZFiles",
        required=False,
    )
    prefix = Manual_Field(
        label="Prefix(es)",
        widget=Tagged_Text_Widget(),
        required=False,
        help_text="Separate with commas. Match order in associated ZFiles.",
    )


class Publication_Pack_Select_Form(forms.Form):
    use_required_attribute = False
    heading = "Select Publication Pack"
    submit_value = "Select"
    pack = forms.ModelChoiceField(queryset=Article.objects.publication_packs())


class Publication_Pack_Share_Form(forms.Form):
    use_required_attribute = False
    reply_ids = {"twitter": "", "mastodon": ""}
    heading = "Share Publication Pack"
    submit_value = "Post"
    attrs = {"method": "POST"}

    ACCOUNTS = (
        ("mastodon", "Mastodon"),
        ("twitter", "Twitter"),
    )

    pack = forms.IntegerField(widget=forms.HiddenInput())
    article_start = forms.IntegerField(initial=0, widget=forms.HiddenInput())
    idx = forms.IntegerField(label="Index", required=False, widget=forms.HiddenInput())
    body = forms.CharField(
        label="Description",
        widget=forms.Textarea(),
        help_text="Body of Post"
    )
    image1 = forms.CharField(label="Image 1", required=False, help_text="Relative to Zfile prefix if path is not absolute")
    image2 = forms.CharField(label="Image 2", required=False, help_text="Relative to Article prefix if path is not absolute")
    image3 = forms.CharField(label="Image 3", required=False, help_text="Relative to Article prefix if path is not absolute")
    image4 = forms.CharField(label="Image 4", required=False, help_text="Relative to Article prefix if path is not absolute")
    twitter_id = forms.CharField(required=False)
    mastodon_id = forms.CharField(required=False)
    zfile_prefix = forms.CharField()
    article_prefix = forms.CharField()

    accounts = forms.MultipleChoiceField(
        required=False, widget=forms.CheckboxSelectMultiple, choices=ACCOUNTS,
        initial=["twitter", "mastodon"],
        help_text="Accounts to post this content to",
    )

    def process(self):
        accounts = self.cleaned_data.get("accounts", False)
        print(accounts)

        for account in accounts:
            if account == "mastodon":
                s = Social_Mastodon()
            elif account == "twitter":
                s = Social_Twitter()

            reply_id = "{}_id".format(account)

            s.login()  # Login
            s.reset_media()
            for i in range(1, 5):  # Upload all media
                self.upload_media(s, i)

            if self.cleaned_data.get(reply_id):  # Set reply ID if one exists
                s.reply_to = self.cleaned_data[reply_id]

            response = s.post(self.cleaned_data.get("body", ""))  # Post
            self.reply_ids[account] = response.get("id", "???")  # Record ID for reply

    def upload_media(self, s, i):
        media_path = ""
        field_value = self.cleaned_data.get("image{}".format(i))
        if not field_value:
            return
        elif not field_value.startswith("/"):
            media_path = os.path.join(APP_ROOT)
            media_path += self.cleaned_data.get("article_prefix") if i != 1 else self.cleaned_data.get("zfile_prefix")
        media_path += field_value
        response = s.upload_media(media_path)


class Stream_VOD_Thumbnail_Generator_Form(forms.Form):
    use_required_attribute = False
    heading = "Stream VOD Thumbnail Generator"
    attrs = {"method": "POST", "enctype": "multipart/form-data"}
    submit_value = "Generate"

    COLOR_CHOICES = (
        ("blue", "Blue"),
        ("green", "Green"),
        ("cyan", "Cyan"),
        ("red", "Red"),
        ("purple", "Purple"),
        ("yellow", "Yellow"),
    )

    TEXT_SIZE_CHOICES = (  # Format = main-font-size:main-text-shadow:sub-font-size:sub-text-shadow
        ("small", "Small"),
        ("medium", "Medium"),
        ("large", "Large"),
    )

    title = forms.CharField(label="Title", required=False)
    subtitle = forms.CharField(label="Subtitle", required=False)
    title_color = forms.ChoiceField(choices=COLOR_CHOICES, widget=Ascii_Color_Widget(choices=COLOR_CHOICES))
    text_size = forms.ChoiceField(choices=TEXT_SIZE_CHOICES, initial="large")

    background_image = Museum_Drag_And_Drop_File_Field(
        widget=UploadFileWidget(target_text="Drag & Drop A File Here or Click to Choose", allowed_preset="image"),
    )

    crop = forms.ChoiceField(label="Background Image Crop", choices=PREVIEW_IMAGE_CROP_CHOICES)


class Tool_ZFile_Select_Form(forms.Form):
    use_required_attribute = False
    key = forms.ModelChoiceField(label="ZFile", queryset=File.objects.tool_zfile_select(), to_field_name="key")
