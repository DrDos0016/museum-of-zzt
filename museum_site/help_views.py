from datetime import date

from django.shortcuts import render
from django.views import View

from museum_site.constants import *
from museum_site.models import *


class Detail_Overview_View(View):
    title = "File Details"
    template_name = "museum_site/help/detail-overview.html"

    def get(self, request, *args, **kwargs):
        context = {
            "title": self.title,
            "details": {"ZZT": [], "SZZT": [], "Media": [], "Other": []},
        }

        details = list(Detail.objects.filter(visible=True).order_by("title"))
        for d in details:
            context["details"][d.category].append(d)

        return render(request, self.template_name, context)


class Genre_Overview_View(View):
    title = "Genre Information"
    template_name = "museum_site/help/genre-overview.html"

    def get(self, request, *args, **kwargs):
        context = {
            "title": self.title,
            "genres": Genre.objects.filter(visible=True).order_by("title"),
        }

        return render(request, self.template_name, context)


def zfiles(request):
    data = {
        "title": "ZFiles Help",
    }

    # Create our example file
    example = File(
        id=999999,
        title="Example ZFile",
        release_date=date.today(),
        letter="z",
        filename="zzt.zip",
        key="zzt",
        size=70700,
        rating=3.14,
        review_count=5,
        article_count=10,
        #screenshot="zzt.png"
    )

    data["example"] = example
    return render(request, "museum_site/help/zfiles.html", data)
