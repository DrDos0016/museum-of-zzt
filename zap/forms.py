import os

from datetime import datetime, timezone, timedelta

from django import forms
from django.conf import settings
from django.template.defaultfilters import date

from museum_site.constants import SITE_ROOT
from museum_site.fields import Museum_Multiple_Choice_Field, Museum_Drag_And_Drop_File_Field
from museum_site.widgets import *
from zap.core import querydict_to_json_str, zap_upload_file, zap_get_social_account
from zap.models import Post

ACCOUNTS = (
    ("bluesky", "Bluesky"),
    ("discord", "Discord"),
    ("mastodon", "Mastodon"),
    ("patreon", "Patreon"),
    ("tumblr", "Tumblr"),
    ("twitter", "Twitter"),
)

DISCORD_CHANNELS = (
    ("announcements", "#Announcements"),
    ("patrons", "#Patrons"),
    ("moz-feed", "#Museum-of-ZZT-Feed"),
    ("test", "#Bot-Dev (Test Announcement)"),
    ("log", "#Bot-Dev (Logging)"),
)

DISCORD_ROLES = (
    ("838135077144625213", "Stream-Alerts-All"),
    ("760545019273805834", "Stream-Alerts-Dos"),
    ("1275156566643048449", "Test Role"),
)
#<@&165511591545143296>


class ZAP_Model_Select_Form(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ZAP_Post_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Post"
    attrs = {"method": "POST"}
    processed = False

    ZAP_POST_SHORTCUTS = (
        ("N/A", "———"),
        ("live", "Live Now"),
        ("schedule", "Stream Schedule - (Check Media 1)"),
        ("vod", "Stream VOD"),
    )


    form_shortcut = forms.ChoiceField(required=False, choices=ZAP_POST_SHORTCUTS, help_text="Select to quickly set up a common post type.")
    title = forms.CharField(help_text="Used as post title on Tumblr.", required=False)
    accounts = Museum_Multiple_Choice_Field(
        required=False, widget=forms.CheckboxSelectMultiple, choices=ACCOUNTS, initial=["discord", "twitter", "tumblr", "mastodon"]
    )
    discord_channel = forms.ChoiceField(choices=DISCORD_CHANNELS, initial=("announcements" if settings.ENVIRONMENT == "PROD" else "test"))
    discord_mentions = Museum_Multiple_Choice_Field(required=False, widget=forms.CheckboxSelectMultiple, choices=DISCORD_ROLES)

    body = forms.CharField(
        widget=Enhanced_Text_Area_Widget(char_limit=10000),
        help_text="Tweets are limited to 240 characters.<br>Bskies are limited to 300 characters.<br>Toots are limited to 500 characters.",
    )
    hashtags = forms.CharField(required=False, help_text="Separate with comma. Prefix with `#` ie: `#zzt, #stream announcement`.")

    media_1 = forms.CharField(required=False, help_text="Should begin with /static/...")
    media_2 = forms.CharField(required=False, help_text="Should begin with /static/...")
    media_3 = forms.CharField(required=False, help_text="Should begin with /static/...")
    media_4 = forms.CharField(required=False, help_text="Should begin with /static/...")

    def smart_start(self, event=None):
        if not event:
            return False
        self.fields["body"].initial = event.prefab_post()

        if event.image_render_datetime:
            self.fields["media_1"].initial = event.get_image_render_url()
        return True

    def process(self, request):
        self.responses = {}

        accounts = self.cleaned_data.get("accounts", [])
        post_responses = {}

        if not self.check_media_exists():
            return False


        for account in accounts:
            self.responses[account] = []
            try:
                s = zap_get_social_account(account)
                reply_id = "{}_id".format(account)

                # Discord needs to specify its channel and mentions
                if account == "discord":
                    s.set_channel_key(self.cleaned_data.get("discord_channel", "test"))
                    s.set_mentions(self.cleaned_data.get("discord_mentions", []))

                s.login()  # Login
                s.reset_media()
                for i in range(1, 5):  # Upload all media
                    response = self.upload_media(s, i)
                    if response:
                        self.responses[account].append(response)

                if self.cleaned_data.get(reply_id, "0") and self.cleaned_data.get(reply_id, "0") != "0":  # Set reply ID if one exists
                    if account == "bluesky":
                        fields = self.cleaned_data[reply_id].split(";")
                        reply_dict = {"uri": fields[0].split("=", 2)[1], "cid": fields[1].split("=", 2)[1]}
                        reply_id = {"parent": reply_dict, "root": reply_dict}
                    response = s.post(self.cleaned_data.get("body", ""), self.cleaned_data.get("title", ""), self.cleaned_data.get("hashtags", []), reply_to=reply_id)
                else:
                    response = s.post(self.cleaned_data.get("body", ""), self.cleaned_data.get("title", ""), self.cleaned_data.get("hashtags", []))
            except:
                response = {"failed": "Failed {}. This is default response within an exception".format(account)}
                self.add_error("accounts", "Failed to post to {}".format(account))

            post_responses[account] = response
            self.responses[account].append(response)

        # Create the Post object
        p = Post()
        p.title = self.cleaned_data.get("title", self.cleaned_data.get("body", "Untitled Post")[:75] + "...")
        p.body = self.cleaned_data.get("body", "")
        p.media_1 = self.cleaned_data.get("media_1", "")
        p.media_2 = self.cleaned_data.get("media_2", "")
        p.media_3 = self.cleaned_data.get("media_3", "")
        p.media_4 = self.cleaned_data.get("media_4", "")
        p.tweet_id = post_responses["twitter"].data.get("id", 0) if "twitter" in accounts else 0
        p.mastodon_id = post_responses["mastodon"].get("id", 0) if "mastodon" in accounts else 0
        p.tumblr_id = post_responses["tumblr"].get("id", 0) if "tumblr" in accounts else 0

        if "bluesky" in accounts:
            bsky_id = "uri={};cid={};".format(post_responses["bluesky"].uri, post_responses["bluesky"].cid)
            p.bluesky_id = bsky_id

        p.save()
        self.processed = True
        self.post_object = p

    def upload_media(self, s, i):
        media_path = ""
        field_value = self.cleaned_data.get("media_{}".format(i))
        if not field_value or not field_value.startswith("/static/"):
            return

        media_path = os.path.join(SITE_ROOT, "museum_site")
        media_path += field_value

        response = s.upload_media(media_path)
        return response

    def check_media_exists(self):
        success = True
        for i in range(1, 5):  # Upload all media
            field_value = self.cleaned_data.get("media_{}".format(i))
            if field_value:
                media_path = os.path.join(SITE_ROOT, "museum_site")
                media_path += field_value
                if not os.path.isfile(media_path):
                    self.add_error("media_{}".format(i), "File not found")
                    success = False
        return success

class ZAP_Reply_Form(ZAP_Post_Form):
    tweet_id = forms.CharField(widget=forms.HiddenInput())
    tumblr_id = forms.CharField(widget=forms.HiddenInput())
    mastodon_id = forms.CharField(widget=forms.HiddenInput())
    bluesky_id = forms.CharField(widget=forms.HiddenInput())

    def smart_start(self, post=None):
        if not post:
            return False

        #del self.fields["accounts"]
        self.fields["title"].initial = "Reply to " + post.title
        self.fields["tweet_id"].initial = post.tweet_id
        self.fields["tumblr_id"].initial = post.tumblr_id
        self.fields["mastodon_id"].initial = post.mastodon_id
        self.fields["bluesky_id"].initial = post.bluesky_id

        return True


class ZAP_Media_Upload_Form(forms.Form):
    use_required_attribute = False
    template_name = "media-upload-form.html"
    heading = "Media Upload"
    submit_value = "Save"
    attrs = {
        "method": "POST",
        "enctype": "multipart/form-data",
    }

    user_upload = Museum_Drag_And_Drop_File_Field(label="Media", widget=UploadFileWidget(target_text="Drag & Drop A File Here or Click to Choose"))
    uploaded_file_name = forms.CharField(required=False, help_text="Alternate name to use for upload")
    optimize_png = forms.BooleanField(initial=True, help_text="Run optipng on upload. (.PNG only)")

    def process(self, request):
        self.uploaded_file_names = []
        for k in request.FILES:
            uploaded_file_name = zap_upload_file(request.FILES[k], self.cleaned_data.get("uploaded_file_name"), self.cleaned_data.get("optimize_png"))
            self.uploaded_file_names.append(uploaded_file_name)


class ZAP_Post_Boost_Form(forms.Form):
    use_required_attribute = False
    heading = "Boost Post"
    submit_value = "Boost"
    attrs = {
        "method": "POST",
    }

    accounts = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=ACCOUNTS)
    post_id = forms.IntegerField()

    def process(self, request):
        post = Post.objects.get(pk=self.cleaned_data["post_id"])
        social_id_dict = post.get_social_id_dict()

        self.responses = {}

        accounts = self.cleaned_data.get("accounts", False)

        for account in accounts:
            self.responses[account] = []
            s = zap_get_social_account(account)

            s.login()  # Login

            response = s.boost(social_id_dict[account])  # Boost
            self.responses[account].append(response)
        self.processed = True


class ZAP_Publication_Pack_Form(forms.Form):
    use_required_attribute = False
    heading = "Publication Pack Form"
    submit_value = "Post"
    attrs = {
        "method": "POST",
    }

    #publication_pack = forms.ModelChoice()
