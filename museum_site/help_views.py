from django.shortcuts import render
from .common import *
from .constants import *
from .models import *

def genres(request):
    data = {}

    return render(request, "museum_site/help/genres.html", data)

def zfiles(request):
    data = {
        "title": "ZFiles Help",
    }

    # Create our example file
    example = File(
        id=999999,
        title="Example ZFile",
        author="Dr. Dos",
        company="Worlds of ZZT",
        release_date=date.today(),
        genre="Adventure/Action/Demo",
        letter="z",
        filename="zzt.zip",
        key="zzt",
        size=70700,
        rating=3.14,
        review_count=5,
        article_count=10,
        screenshot="zzt.png"
    )

    data["list_table_header"] = table_header(File.table_fields)
    data["example"] = example
    return render(request, "museum_site/help/zfiles.html", data)
