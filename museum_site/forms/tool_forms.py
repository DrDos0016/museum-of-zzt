import base64
import glob
import json
import os
import time
import tempfile
import zipfile

import requests

from django import forms
from django.core.cache import cache
from django.template.defaultfilters import linebreaks, urlize
from django.template.loader import render_to_string

from internetarchive import upload as ia_upload

from museum_site.core.file_utils import delete_this
from museum_site.core.image_utils import crop_file, optimize_image
from museum_site.core.social import Social_Twitter, Social_Mastodon
from museum_site.constants import APP_ROOT, DATA_PATH, STATIC_PATH, ENV
from museum_site.settings import (
    IA_ACCESS, IA_SECRET, DISCORD_WEBHOOK_ANNOUNCEMENTS_URL, DISCORD_WEBHOOK_PATRONS_URL, DISCORD_WEBHOOK_TEST_URL, DISCORD_WEBHOOK_FEED_URL,
)
from museum_site.fields import (
    Enhanced_Model_Choice_Field, Manual_Field, Museum_Drag_And_Drop_File_Field, Museum_Model_Scrolling_Multiple_Choice_Field, Museum_Tagged_Model_Choice_Field,
    Museum_Tagged_Text_Field, Museum_Choice_Field
)
from museum_site.models import Article, Content, Download, File, Series
from museum_site.widgets import (
    Ascii_Color_Widget,
    Enhanced_Date_Widget, Enhanced_Text_Widget, Ordered_Scrolling_Radio_Widget, Scrolling_Checklist_Widget, Tagged_Text_Widget, UploadFileWidget
)


PREVIEW_IMAGE_CROP_CHOICES = (
    ("ZZT", "480x350 ZZT Board"),
    ("SZZT", "448x400 Super ZZT Board"),
    ("NONE", "Do Not Crop Image"),
)

class Checksum_Comparison_Form(forms.Form):
    use_required_attribute = False
    heading = "Checksum Comparison"
    attrs = {"method": "POST"}
    submit_value = "Compare"

    checksums = forms.CharField(label="Checksums", widget=forms.Textarea(), help_text="One checksum per line. Chars past the md5 are truncated so you can copy/paste md5sum's results directly.")
    checksum_type = Museum_Choice_Field(
        label="Checksum Type",
        widget=forms.RadioSelect(),
        choices=(
            ("md5", "md5 - Used for zip files"),
            ("crc32", "crc32 - Used for files within zip files")
        ),
        initial="md5"
    )

    def clean_checksums(self):
        raw_checksums = self.cleaned_data["checksums"].split("\r\n")
        checksums = []
        for c in raw_checksums:
            checksums.append(c[:32])
        return checksums

    def process(self):
        checksums = self.cleaned_data["checksums"]
        if self.cleaned_data["checksum_type"] == "md5":
            qs = File.objects.filter(checksum__in=checksums).order_by("sort_title")
        else:
            qs = Content.objects.filter(crc32__in=checksums).values_list("pk", flat=True)
            pks = list(qs)
            qs = File.objects.filter(content__id__in=pks).order_by("sort_title")
        return {"matches": qs}

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
        ("log", "Logging (#bot-dev)"),
    )

    channel = forms.ChoiceField(choices=CHANNELS, initial="announcements")
    body = forms.CharField(
        label="Body",
        widget=forms.Textarea(),
        help_text="Discord Markdown supported"
    )
    image_embeds = forms.CharField(
        required=False,
        label="Image embeds",
        widget=forms.Textarea(),
        help_text="One URL per line. 10 Maximum embeds (unverified).<br>Ex: https://museumofzzt.com/static/screenshots/1000/zzt.png",
    )

    def clean_image_embeds(self):
        embeds = self.cleaned_data["image_embeds"].split("\r\n")
        return embeds

    def process(self):
        destinations = {
            "announcements": DISCORD_WEBHOOK_ANNOUNCEMENTS_URL, "patrons": DISCORD_WEBHOOK_PATRONS_URL, "moz-feed": DISCORD_WEBHOOK_FEED_URL,
            "test": DISCORD_WEBHOOK_TEST_URL, "log": DISCORD_WEBHOOK_TEST_URL,
        }
        destination_webhook = destinations.get(self.cleaned_data["channel"])

        discord_data = {"content": self.cleaned_data["body"]}

        if self.cleaned_data["image_embeds"]:
            embeds = []
            for embed in self.cleaned_data["image_embeds"]:
                embeds.append({"image": {"url": embed}})
            discord_data["embeds"] = embeds

        resp = requests.post(destination_webhook, headers={"Content-Type": "application/json"}, data=json.dumps(discord_data))
        self.response = resp

    def send_message(self, channel, body, image_embeds=[]):
        # TODO: Is this too hacky?
        if ENV == "PROD":
            self.cleaned_data = {"channel": channel, "body": body, "image_embeds": image_embeds}
            self.process()
        else:
            print("Faux Logging to #{} -- {}".format(channel, body))

class Download_Form(forms.ModelForm):
    user_required_attribute = False
    attrs = {"method": "POST"}
    submit_value = "Add New Download"

    class Meta:
        model = Download
        fields = ["url", "kind", "hosted_text"]


class IA_Mirror_Form(forms.Form):
    heading = "Internet Archive Mirroring"
    submit_value = "Mirror File"
    attrs = {"method": "POST", "enctype": "multipart/form-data"}
    use_required_attribute = False
    required = False

    log = []

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
        widget=UploadFileWidget(target_text="Drag & Drop a Zip File Here or Click to Choose")
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
        self.log.append("{}: Initiating mirroring process\n".format(int(time.time())))
        archive_title = self.cleaned_data["title"]
        self.log.append("{}: Mirorring `{}`\n".format(int(time.time()), archive_title))
        self.log.append("{}: Using Collection `{}`\n".format(int(time.time()), self.cleaned_data["collection"]))
        # Copy the file's zip into a temp directory
        if self.cleaned_data["collection"] == "test_collection":
            ts = str(int(time.time()))
            wip_zf_name = "test_" + ts + "_" + self.cleaned_data["filename"]
            archive_title = "Test - " + ts + "_" + archive_title
            url = "test_" + ts + "_" + self.cleaned_data["url"]
        else:
            wip_zf_name = self.cleaned_data["filename"]
            url = self.cleaned_data["url"]
        self.log.append("{}: Working with WIP Zipfile `{}`\n".format(int(time.time()), wip_zf_name))
        self.log.append("{}: URL: `{}`\n".format(int(time.time()), url))

        temp_dir = tempfile.TemporaryDirectory(prefix="moz-ia")
        wip_dir = temp_dir.name
        wip_zf_path = os.path.join(wip_dir, wip_zf_name)

        self.log.append("{}: Created temp directory `{}`\n".format(int(time.time()), temp_dir))

        # Create a ZZT.CFG if parameters were specified
        if self.cleaned_data["zzt_config"]:
            with open(os.path.join(wip_dir, "ZZT.CFG"), "w") as fh:
                fh.write(self.cleaned_data["zzt_config"])
            self.log.append("{}: Added custom `ZZT.CFG` file to archive.\n".format(int(time.time())))
        else:
            self.log.append("{}: Skipped adding a `ZZT.CFG` file to archive.\n".format(int(time.time())))

        # Extract zfile if not using an alternate zip
        if self.cleaned_data["zfile"]:
            zf = zipfile.ZipFile(files["zfile"])
            self.log.append("{}: Using alternate zip archive for zfile: `{}`\n".format(int(time.time()), self.cleaned_data["zfile"]))
        else:
            zf = zipfile.ZipFile(zfile.phys_path())
            self.log.append("{}: Using zgames zip archive for zfile: `{}`\n".format(int(time.time()), zfile.phys_path()))

        files = zf.infolist()
        comment = zf.comment
        for f in files:
            zf.extract(f, path=wip_dir)
            timestamp = time.mktime(f.date_time + (0, 0, -1))
            os.utime(os.path.join(wip_dir, f.filename), (timestamp, timestamp))
        zf.close()
        self.log.append("{}: Extracted {} files to temp directory.\n".format(int(time.time()), len(files)))

        # Extract any additional packages
        self.log.append("{}: Adding additional packages to archive\n".format(int(time.time())))
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
            self.log.append("{}: -- Added package `{}`\n".format(int(time.time()), package_path))

        # Add to WIP archive
        self.log.append("{}: Adding zgame/alt archive contents to IA archive zipfile\n".format(int(time.time())))
        package_files = glob.glob(os.path.join(wip_dir, "**"), recursive=True)
        zf = zipfile.ZipFile(wip_zf_path, "w")
        for f in package_files:
            base = f.replace(wip_dir, "")[1:]  # Trim trailing /
            if base:
                #print("Adding to wip archive:", f, "as", base)
                zf.write(f, arcname=base)
                self.log.append("{}: Adding `{}` to IA archive zipfile as `{}`\n".format(int(time.time()), f, base))
        if comment:
            zf.comment = comment
            self.log.append("{}: Added zipfile comment\n".format(int(time.time())))
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

        self.log.append("{}: Finalized metadata:\n{}\n".format(int(time.time()), str(meta)))

        # Mirror the file
        self.log.append("{}: Begin Upload of `{}`\n".format(int(time.time()), wip_zf_path))

        r = ia_upload(
            url,
            files=[wip_zf_path],
            metadata=meta,
            access_key=IA_ACCESS,
            secret_key=IA_SECRET,
        )
        self.mirror_status = "SUCCESS" if (r[0].status_code == 200) else "FAILED"
        self.log.append("{}: IA RESPONSE [{}] [Status Code {}][Content {}]\n".format(int(time.time()), self.mirror_status, r[0].status_code, r[0].content))


        # Remove the working files/folders
        self.log.append("{}: Removing temp dir `{}`\n".format(int(time.time()), wip_dir))
        delete_this(wip_dir)


class Series_Form(forms.ModelForm):
    user_required_attribute = False
    attrs = {"method": "POST", "enctype": "multipart/form-data"}
    submit_value = "Add Series"

    associations = Museum_Model_Scrolling_Multiple_Choice_Field(
        label="Associated Articles",
        required=False,
        queryset=Article.objects.accessible(),
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


class Video_Description_Form(forms.Form):
    heading = "Video Description Generator"
    use_required_attribute = False
    submit_value = "Select"

    VIDEO_TYPE_CHOICES = (
        ("Livestream", "Livestream VOD"),
        ("Playthrough", "Playthrough - No Commentary"),
    )

    kind = forms.ChoiceField(label="Video Type", choices=VIDEO_TYPE_CHOICES)

    associated = Museum_Tagged_Model_Choice_Field(
        widget=Ordered_Scrolling_Radio_Widget(),
        queryset=File.objects.all(),
        label="Associated ZFiles",
        help_text="Select one or more ZFiles",
        required=False,
    )
    stream_date = forms.CharField(
        widget=forms.DateInput(attrs={"type": "date"}),
        help_text="Date of original livestream (VOD only)",
        required=False
    )

    timestamp = Museum_Tagged_Text_Field(
        label="Timestamp(s)",
        required=False,
        help_text="Separate with commas. Match order in associated ZFiles. (VOD only)",
    )


class Livestream_Vod_Form(forms.Form):
    use_required_attribute = False
    heading = "Add Livestream VOD"
    submit_value = "Add Livestream VOD"
    attrs = {"method": "POST", "enctype": "multipart/form-data"}

    CATEGORY_CHOICES = (
        ("Livestream", "Livestream"),
        ("Let's Play", "Let's Play"),
        ("Playthrough", "Playthrough"),
        ("Misc", "Misc."),
    )

    TITLE_PREFIX_REFERENCE = """
    <div style="font-size:10pt;">
        Let's Play - ♦ Livestream -♦
        Wildcard Stream Vol. ### - ♦ Bonus Stream - ♦
        Full Playthrough - ♦
    </div>
    """

    category = forms.ChoiceField(label="Category", choices=CATEGORY_CHOICES, help_text="Article model category")
    author = forms.CharField(initial="Dr. Dos")
    title = forms.CharField(widget=Enhanced_Text_Widget(char_limit=80), help_text="Used exactly as entered. Remember to prefix!{}".format(TITLE_PREFIX_REFERENCE))
    date = forms.DateField(widget=Enhanced_Date_Widget(buttons=["today"]))
    video_url = forms.URLField(help_text=(
            "https://youtu.be/<b>{id}</b>, <br>https://www.youtube.com/watch?v=<b>{id}</b>&feature=youtu.be, <br>"
            "or https://studio.youtube.com/video/<b>{id}</b>/edit format. Add multiplate with commas (no space)."
        ),
        label="Video URL"
    )
    video_description = forms.CharField(
        widget=forms.Textarea(),
        help_text="Copy/Paste from YouTube video details editor. Everything below the '=====' will be truncated"
    )
    description = forms.CharField(widget=Enhanced_Text_Widget(char_limit=250), label="Article Summary")
    preview_image = Museum_Drag_And_Drop_File_Field(
        help_text="Select the image you wish to upload.",
        label="Preview Image",
        widget=UploadFileWidget(target_text="Drag & Drop A File Here or Click to Choose", allowed_preset="image"),
    )
    crop = forms.ChoiceField(label="Preview Image Crop", choices=PREVIEW_IMAGE_CROP_CHOICES, initial="NONE")
    publication_status = forms.ChoiceField(choices=Article.PUBLICATION_STATES)
    series = forms.ModelChoiceField(queryset=Series.objects.visible_incomplete_priority(), empty_label="- NONE -", required=False, help_text="Create a <a href='/tools/series/add/' target='_blank'>new series</a>")
    associated_zfile = Museum_Model_Scrolling_Multiple_Choice_Field(
        label="Associated ZFiles",
        required=False,
        queryset=File.objects.all(),
        widget=Scrolling_Checklist_Widget(
            buttons=["Clear"],
            show_selected=True,
        )
    )

    def clean_video_url(self):
        videos = self.cleaned_data["video_url"].split(",")
        video_urls = []

        for video_url in videos:
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
        video_description = self.cleaned_data["video_description"].strip()
        if "====================" in video_description:
            video_description = video_description[:video_description.find("====================")]
        return video_description

    def create_article(self):
        preview_image = self.files["preview_image"]

        # Prepare the Article
        a = Article()
        key = ("pk-" + str(self.cleaned_data["associated_zfile"][0].pk)) if self.cleaned_data["associated_zfile"] else "no-assoc"
        prefix = {"Livestream": "ls", "Let's Play": "lp", "misc": "x", "playthrough": "pt"}.get(self.cleaned_data["category"], "ls")
        a.title = self.cleaned_data["title"]
        a.author = self.cleaned_data["author"]
        a.category = self.cleaned_data["category"]
        a.schema = "django"
        a.publish_date = self.cleaned_data["date"]
        a.published = self.cleaned_data["publication_status"]
        a.description = self.cleaned_data["description"]
        a.static_directory = "{}-{}-{}".format(prefix, key, self.cleaned_data["video_url"][0])
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
            fa = File.objects.get(pk=file_association.pk)
            fa.articles.add(a)
            fa.save()  # FULLSAVE

        # Associate the article with the selected series (if any)
        if self.cleaned_data["series"]:
            a.series.add(self.cleaned_data["series"])
            a.save()

        return a

class Manage_Cache_Form(forms.Form):
    use_required_attribute = False
    attrs = {"method": "POST"}
    submit_value = "Set Cache Entry"

    KNOWN_CACHE_KEYS = (
        ("UPLOAD_QUEUE_SIZE", "Upload Queue Size"),
        ("DISCORD_LAST_ANNOUNCED_FILE_NAME", "Discord Last Announced File Name"),
        ("ENV", "Environment"),
        ("CHARSETS", "Character Sets"),
        ("CUSTOM_CHARSETS", "Custom Character Sets"),
        ("STRAWPOLL_STREAM_VOTE", "Strawpoll Stream Vote URL"),
    )

    key = forms.ChoiceField(label="Cache Key", choices=KNOWN_CACHE_KEYS)
    value = forms.CharField(widget=forms.Textarea(), required=False)

    def process(self):
        key = self.cleaned_data["key"].upper()
        value = self.cleaned_data["value"]
        cache.set(key, value)
        return True


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
    prefix = Museum_Tagged_Text_Field(
        label="Screenshot Prefixes",
        required=False,
        help_text="Separate with commas. Match order in associated ZFiles.",
    )

class Publication_Pack_Select_Form(forms.Form):
    use_required_attribute = False
    heading = "Select Publication Pack"
    submit_value = "Select"
    pack = forms.ModelChoiceField(queryset=Article.objects.publication_packs())


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
        ("white", "White"),
        ("transparent", "transparent"),
    )

    TEXT_SIZE_CHOICES = (
        ("small", "Small"),
        ("medium", "Medium"),
        ("large", "Large"),
        ("xl", "XL"),
    )

    CRITTER_CHOICES = (
        ("ZZT", "ZZT"),
        ("SZZT", "Super ZZT"),
        ("MZX", "MegaZeux"),
    )

    FORM_SHORTCUTS = (
        ("N/A", "———"),
        ("playthrough", "Playthrough"),
        ("vod", "Standard VOD"),
        ("wildcard", "Wildcard Stream"),
    )

    form_shortcut = forms.ChoiceField(required=False, choices=FORM_SHORTCUTS, help_text="Select to quickly set up common form values.")
    title = forms.CharField(label="Title", required=False)
    subtitle = forms.CharField(label="Subtitle", required=False, help_text="`Part ` will be ignored.")
    title_color = forms.ChoiceField(choices=COLOR_CHOICES, widget=Ascii_Color_Widget(choices=COLOR_CHOICES))
    text_size = forms.ChoiceField(choices=TEXT_SIZE_CHOICES, initial="large")

    background_image = Museum_Drag_And_Drop_File_Field(
        widget=UploadFileWidget(target_text="Drag & Drop A File Here or Click to Choose", allowed_preset="image"),
    )

    critters = forms.ChoiceField(choices=CRITTER_CHOICES, initial="ZZT")

    crop = forms.ChoiceField(label="Background Image Crop", choices=PREVIEW_IMAGE_CROP_CHOICES)
    wide = forms.ChoiceField(choices=(("wide", "16:9"), ("standard", "4:3")), initial="standard")


class Tool_ZFile_Select_Form(forms.Form):
    use_required_attribute = False
    key = forms.ModelChoiceField(label="ZFile", queryset=File.objects.tool_zfile_select(), to_field_name="key")
