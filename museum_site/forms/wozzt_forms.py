from django import forms

from museum_site.models import WoZZT_Queue

class WoZZT_Roll_Form(forms.Form):
    use_required_attribute = False
    attrs = {"method": "POST"}
    submit_value = "Roll"

    action = forms.CharField(initial="roll", widget=forms.HiddenInput())
    count = forms.IntegerField(label="Quantity", initial=25)
    category = forms.ChoiceField(
        label="Category",
        choices=(
            ("wozzt", "Worlds of ZZT"),
            ("tuesday", "Title Screen Tuesday"),
            ("discord", "Discord Queue"),
        )
    )


    def process(self):
        count = self.cleaned_data["count"]
        category = self.cleaned_data["category"]
        title_screen = True if category == "tuesday" else False

        for x in range(0, count):
            WoZZT_Queue().roll(category=category, title_screen=title_screen)
