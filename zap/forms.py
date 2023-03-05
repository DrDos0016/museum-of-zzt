import os

from datetime import datetime, timezone, timedelta

from django import forms
from django.template.defaultfilters import date

from museum_site.core.social import Social_Mastodon, Social_Twitter
from museum_site.constants import SITE_ROOT
from museum_site.widgets import *
from zap.core import querydict_to_json_str, zap_upload_file
from zap.models import Event

ACCOUNTS = (
    ("twitter", "Twitter"),
    ("tumblr", "Tumblr"),
    ("mastodon", "Mastodon"),
    ("patreon", "Patreon"),
    ("discord", "Discord"),
    ("cohost", "Cohost"),
)


class ZAP_Post_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Post"
    attrs = {"method": "POST"}
    processed = False

    accounts = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=ACCOUNTS)

    body = forms.CharField(
        widget=Enhanced_Text_Area_Widget(char_limit=10000),
        help_text="Tweets are limited to 240 characters.<br>Toots are limited to 500 characters.",
    )

    media_1 = forms.CharField(required=False)
    media_2 = forms.CharField(required=False)
    media_3 = forms.CharField(required=False)
    media_4 = forms.CharField(required=False)

    def smart_start(self, event=None):
        if not event:
            return False
        print("Starting with event", event)

        self.fields["body"].initial = event.prefab_post()

        if event.image_render_datetime:
            self.fields["media_1"].initial = event.get_image_render_url()
        return True

    def process(self, request):
        self.responses = {}
        print("Processing ZAP Post Form")

        accounts = self.cleaned_data.get("accounts", False)
        print(accounts)

        for account in accounts:
            self.responses[account] = []
            if account == "mastodon":
                s = Social_Mastodon()
            elif account == "twitter":
                s = Social_Twitter()

            reply_id = "{}_id".format(account)

            s.login()  # Login
            s.reset_media()
            for i in range(1, 5):  # Upload all media
                response = self.upload_media(s, i)
                if response:
                    self.responses[account].append(response)

            #if self.cleaned_data.get(reply_id):  # Set reply ID if one exists
            #    s.reply_to = self.cleaned_data[reply_id]

            response = s.post(self.cleaned_data.get("body", ""))  # Post
            self.responses[account].append(response)
        self.processed = True

    def upload_media(self, s, i):
        media_path = ""
        field_value = self.cleaned_data.get("media_{}".format(i))
        if not field_value or not field_value.startswith("/static/zap/"):
            return

        media_path = os.path.join(SITE_ROOT, "museum_site")
        media_path += field_value

        response = s.upload_media(media_path)
        return response


class ZAP_Media_Upload_Form(forms.Form):
    use_required_attribute = False
    template_name = "media-upload-form.html"
    heading = "Media Upload"
    submit_value = "Save"
    attrs = {
        "method": "POST",
        "enctype": "multipart/form-data",
    }

    user_upload = forms.FileField(required=False, label="Media", widget=UploadFileWidget(target_text="Drag & Drop Media Here or Click to Choose"))
    uploaded_file_name = forms.CharField(required=False, help_text="Alternate name to use for upload")

    def process(self, request):
        for k in request.FILES:
            print(request.FILES[k])
            zap_upload_file(request.FILES[k], self.cleaned_data.get("uploaded_file_name"))


class ZAP_Create_Stream_Schedule_Form(forms.Form):
    FORM_VERSION = 1
    template_name = "stream-schedule-form.html"
    use_required_attribute = False
    heading = "Create Stream Schedule"
    submit_value = "Save"
    attrs = {
        "method": "POST",
        "enctype": "multipart/form-data",
    }

    extra_buttons = ["<input type='button' id='preview' value='Preview'>", "<input type='submit' name='copy' id='copy' value='Save Copy'>"]

    version = forms.IntegerField(widget=forms.HiddenInput(), initial=FORM_VERSION)

    date_start = forms.CharField()
    date_end = forms.CharField()

    date_1 = forms.CharField(required=False, label="Starting Date")
    time_1 = forms.CharField(required=False, label="Starting Time")
    title_1 = forms.CharField(required=False)
    desc_1 = forms.CharField(required=False, widget=forms.Textarea(), label="Description")
    media_1 = forms.CharField(required=False)

    date_2 = forms.CharField(required=False, label="Starting Date")
    time_2 = forms.CharField(required=False, label="Starting Time")
    title_2 = forms.CharField(required=False)
    desc_2 = forms.CharField(required=False, widget=forms.Textarea(), label="Description")
    media_2 = forms.CharField(required=False)

    date_3 = forms.CharField(required=False, label="Starting Date")
    time_3 = forms.CharField(required=False, label="Starting Time")
    title_3 = forms.CharField(required=False)
    desc_3 = forms.CharField(required=False, widget=forms.Textarea(), label="Description")
    media_3 = forms.CharField(required=False)

    def __init__(self, data=None, initial=None):
        super().__init__(data, initial)
        print("init")

    def smart_start(self):
        today = datetime.now(timezone.utc)

        # Assume Today is Monday and end on Sunday
        self.fields["date_start"].initial = date(today, "M jS")
        self.fields["date_end"].initial = date(today + timedelta(days=6), "M jS")

        # Friday 6pm Pacific
        self.fields["date_1"].initial = date(today + timedelta(days=4), "l M j")
        self.fields["time_1"].initial = "6:00pm PST / 9:00pm EST / 02:00 UTC"

        # Sunday Noon Pacific
        self.fields["date_2"].initial = date(today + timedelta(days=6), "l M j")
        self.fields["time_2"].initial = "Noon PST / 3:00pm EST / 20:00 UTC"
        self.fields["title_2"].initial = "Wildcard Stream: "
        return True

    def process(self, request):
        print("Processing...")

        json_str = querydict_to_json_str(request.POST)
        if request.GET.get("pk") and not request.POST.get("copy"):  # Saving an existing form as a non-copy
            event = Event.objects.get(pk=request.GET["pk"])
        else:
            event = Event()

        event.title = "Stream Schedule for {} through {}".format(request.POST.get("date_start", "?"), request.POST.get("date_end", "?"))
        event.kind = "stream-schedule"
        event.json_str = json_str
        event.save()
