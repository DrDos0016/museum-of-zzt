import os

from datetime import datetime

from django.shortcuts import render

from museum_site.common import *
from museum_site.constants import *
from museum_site.core.file_utils import serve_file_as
from museum_site.models import *
from museum_site.forms import *


def debug(request, filename=None):
    data = {"title": "DEBUG PAGE"}
    data["ARTICLE_DEBUG"] = True
    data["TODO"] = "TODO"  # Expected TODO usage.
    data["CROP"] = "CROP"

    if filename == "saves.html":
        return debug_saves(request)

    f = File.objects.get(pk=int(request.GET.get("id", 420)))
    s = Series.objects.get(pk=10)

    test_wozzt = WoZZT_Queue.objects.filter(
        id__in=[8317, 8318]
    )

    test_reviews = Review.objects.filter(
        id__in=[1700, 1701, 1702, 1703, 100, 200, 300, 1720, 926]
    )

    test_zfiles = File.objects.filter(
        id__in=[278, 327, 420, 1271, 1662, 435, 310, 2367, 2876, 1240, 2095, 3415, 3471, 2568, 9999, 3798, 3480, 874]
    ).order_by("id")

    test_articles = Article.objects.filter(
        id__in=[830, 677, 827, 835, 425, 453, 659, 672, 683, 690]
    ).order_by("-id")

    test_series = Series.objects.filter(
        id__in=[10, 11, 12, 1]
    ).order_by("-id")

    test_collections = Collection.objects.filter(
        id__in=[9, 10, 2, 4, 1, 6]
    ).order_by("-id")

    test_collection_contents = Collection_Entry.objects.filter(collection_id=2).order_by("-id")

    data["available_views"] = ["detailed", "list", "gallery"]
    data["view"] = "detailed"

    data["wozzt"] = test_wozzt
    data["reviews"] = test_reviews
    data["zfiles"] = test_zfiles
    data["articles"] = test_articles
    data["series"] = test_series
    data["collections"] = test_collections
    data["collection_contents"] = test_collection_contents
    data["show"] = request.GET.get("show", "zfiles")

    # Widget Debug
    #data["checklist_items"] = File.objects.published()

    if request.GET.get("serve"):
        return serve_file_as(request.GET.get("serve"), request.GET.get("as", ""))

    if filename:
        return render(
            request, "museum_site/debug/{}.html".format(filename), data
        )
    else:
        return render(request, "museum_site/debug/debug.html", data)


def debug_article(request, fname=""):
    data = {"id": 0}
    data["TODO"] = "TODO"  # Expected TODO usage.
    data["CROP"] = "CROP"

    fname = request.GET.get("file", fname)

    try:
        pk = int(fname)
    except ValueError:
        pk = 0

    if pk:  # Debug existing article
        article = Article.objects.get(pk=pk)
    else:  # Debug WIP article
        if not fname or fname == "<str:fname>":  # Blank/test values
            return redirect("index")

        filepath = os.path.join(SITE_ROOT, "wip", fname)
        if not os.path.isfile(filepath):
            filepath = "/media/drdos/Thumb16/projects/" + request.GET.get("file")

        with open(filepath) as fh:
            article = Article.objects.get(pk=2)
            article.title = filepath
            article.category = "TEST"
            article.static_directory = fname[:-5]
            article.content = fh.read().replace(
                "<!--Page-->", "<hr><b>PAGE BREAK</b><hr>"
            )
            article.publish_date = datetime.now()
            article.schema = request.GET.get("format", "django")
        data["file_path"] = filepath

    data["article"] = article
    data["veryspecial"] = True
    data["title"] = "WIP {} [{} words]".format(fname, article.word_count())
    return render(request, "museum_site/tools/article-wip.html", data)





def debug_widgets(request):
    context = {}

    if request.method == "POST":
        context["form"] = Debug_Form(request.POST)
    else:
        context["form"] = Debug_Form()

    return render(request, "museum_site/debug/debug-widget.html", context)


def debug_play(request):
    context = {}

    if request.GET:
        context["form"] = Zeta_Advanced_Form(request.GET)
    else:
        context["form"] = Zeta_Advanced_Form()

    return render(request, "museum_site/debug/debug-play.html", context)


class Debug_Form(forms.Form):
    use_required_attribute = False
    manual_fields = ["board", "associated", "ssv_author", "rating"]

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
                joined = ",".join(raw) + ","
                if len(joined) > 1:
                    self.fields[field].widget.manual_data["tags_as_string"] = joined
