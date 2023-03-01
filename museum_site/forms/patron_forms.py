from django import forms

from museum_site.constants import EMAIL_ADDRESS

PATRON_DISCLAIMER_TEXT = (
    "This data isn't parsed in any way, so you may write anything you like as long as it can be understood by <a href='mailto:{}'>Dr. Dos</a>.<br><br> "
    "If your suggestion cannot be used for whatever reason (due to an author's request or some other conflict) you will be contacted. Selections will be "
    "used in the order they appear here if applicable."
)


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
        widget=forms.RadioSelect(choices=(("show", "Show patron status"), ("hide", "Hide patron status"))),
        choices=(("show", "Show patron status"), ("hide", "Hide patron status")),
        label="Patronage Visibility"
    )


class Change_Patron_Crediting_Preferences_Form(forms.Form):
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
    stream_poll_nominations = forms.CharField(widget=forms.Textarea(), label="Nominations", help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS))


class Change_Patron_Stream_Selections_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Stream Selections"
    heading = "Change Stream Selections"
    attrs = {"method": "POST"}
    stream_selections = forms.CharField(widget=forms.Textarea(), label="Stream Selections", help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS))


class Change_Patron_Closer_Look_Poll_Nominations_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Closer Look Poll Nominations"
    heading = "Change Closer Look Poll Nominations"
    attrs = {"method": "POST"}

    closer_look_nominations = forms.CharField(
        widget=forms.Textarea(),
        label="Closer Look Poll Nominations",
        help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS)
    )


class Change_Patron_Guest_Stream_Selections_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Guest Stream Selections"
    heading = "Change Guest Stream Selections"
    attrs = {"method": "POST"}
    guest_stream_selections = forms.CharField(widget=forms.Textarea(), label="Guest Stream Selections", help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS))


class Change_Patron_Closer_Look_Selections_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change Closer Look Selections"
    heading = "Change Closer Look Selections"
    attrs = {"method": "POST"}
    closer_look_selections = forms.CharField(widget=forms.Textarea(), label="Closer Look Selections", help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS))


class Change_Patron_Bkzzt_Topics_Form(forms.Form):
    use_required_attribute = False
    submit_value = "Change BKZZT Topics"
    heading = "Change BKZZT Topics"
    attrs = {"method": "POST"}
    bkzzt_topics = forms.CharField(widget=forms.Textarea(), label="BKZZT Topic Selections", help_text=PATRON_DISCLAIMER_TEXT.format(EMAIL_ADDRESS))
