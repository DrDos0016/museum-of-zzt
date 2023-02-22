import os

from datetime import datetime, timezone, timedelta

from django import forms
from django.template.defaultfilters import date

from museum_site.widgets import *

ACCOUNTS = (
    ("twitter", "Twitter"),
    ("tumblr", "Tumblr"),
    ("mastodon", "Mastodon"),
    ("patreon", "Patreon"),
    ("discord", "Discord"),
    ("cohost", "Cohost"),
)

ZAP_UPLOAD_PATH = "/var/projects/museum-of-zzt/museum_site/static/zap/media/"


class ZAP_Form(forms.Form):
    use_required_attribute = False
    heading = "Social Media Shotgun"
    submit_value = "Post"
    attrs = {"method": "POST"}

    body = forms.CharField(
        widget=Enhanced_Text_Area_Widget(char_limit=9999),
        help_text="Tweets are limited to 240 characters.<br>Toots are limited to 500 characters.",
    )

    media = forms.FileField(
        required=False,
        help_text="Select the media you wish to upload.",
        label="Media", widget=UploadFileWidget(target_text="Drag & Drop Media Here or Click to Choose")
    )

    accounts = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=ACCOUNTS)


class ZAP_Stream_Schedule_Form(forms.Form):
    FORM_VERSION = 1
    use_required_attribute = False
    heading = "Social Media Shotgun"
    submit_value = "Save"
    attrs = {
        "method": "POST",
        "enctype": "multipart/form-data",
    }

    extra_buttons = ["<input type='button' id='preview' value='Preview'>"]

    version = forms.IntegerField(widget=forms.HiddenInput(), initial=FORM_VERSION)

    date_start = forms.CharField()
    date_end = forms.CharField()

    date_1 = forms.CharField(required=False, label="Starting Date")
    time_1 = forms.CharField(required=False, label="Starting Time")
    title_1 = forms.CharField(required=False)
    desc_1 = forms.CharField(required=False, widget=forms.Textarea(), label="Description")
    image_1 = forms.FileField(required=False,)

    date_2 = forms.CharField(required=False, label="Starting Date")
    time_2 = forms.CharField(required=False, label="Starting Time")
    title_2 = forms.CharField(required=False)
    desc_2 = forms.CharField(required=False, widget=forms.Textarea(), label="Description")
    image_2 = forms.FileField(required=False)

    date_3 = forms.CharField(required=False, label="Starting Date")
    time_3 = forms.CharField(required=False, label="Starting Time")
    title_3 = forms.CharField(required=False)
    desc_3 = forms.CharField(required=False, widget=forms.Textarea(), label="Description")
    image_3 = forms.FileField(required=False)

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
        print(request)
        print(request.POST)
        print(request.FILES)

        for k in request.FILES:
            uploaded_file = request.FILES[k]
            print("Uploading...", uploaded_file.name)
            with open(os.path.join(ZAP_UPLOAD_PATH, uploaded_file.name), "wb+") as fh:
                for chunk in uploaded_file.chunks():
                    fh.write(chunk)
            print("Wrote file: ", os.path.join(ZAP_UPLOAD_PATH, uploaded_file.name))

        print("PROCESSING FORM!")
