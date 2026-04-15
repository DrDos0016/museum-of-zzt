from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from museum_site.core.misc import Meta_Tag_Block
from museum_site.core.transforms import qs_manual_order
from museum_site.models import File, Article
from stream.models import Stream, Stream_Entry

# Create your views here.
@staff_member_required
def index(request):
    context = {"title": "Stream"}
    return render(request, "stream/index.html", context)


def title_screen_background(request):
    context = {}

    seed = request.GET.get("seed", str(datetime.now()))
    qs = File.objects.roulette(seed, 101).order_by("id")
    context["qs"] = qs
    return render(request, "stream/title-screen-background.html", context)


def overview(request):
    context = {}
    #context["zfiles"] = qs_manual_order(File.objects.filter(pk__in=request.GET.getlist("pk")), request.GET.getlist("pk"))
    if request.GET.get("pk"):
        stream = Stream.objects.filter(pk=request.GET["pk"]).first()
    elif request.GET.get("key"):
        stream = Stream.objects.filter(key=request.GET["key"]).first()
    else:
        today = str(datetime.now())[:10]
        stream = Stream.objects.filter(when__gte=today).first()
    context["stream"] = stream
    context["entries"] = stream.entries.all() if stream else []
    if len(context["entries"]) == 1:
        display_format = "solo"
    elif len(context["entries"]) <= 5:
        display_format = "one-column"
    else:
        display_format = "multi-column"
    context["display_format"] = display_format
    return render(request, "stream/overview.html", context)


def scene_ad_break(request):
    context = {}

    context["articles"] = Article.objects.published().exclude(category="Livestream").order_by("-publish_date")[:2]
    return render(request, "stream/scene/ad-break.html", context)



class Stream_Detail_View(DetailView):
    model = Stream

    def get_queryset(self):
        qs = Stream.objects.filter(pk=self.kwargs["pk"])
        return qs


class Stream_Schedule_View(ListView):
    model = Stream

    def get_queryset(self):
        today = datetime.now()
        qs = Stream.objects.filter(visible=True, when__gte=today).order_by("when")
        return qs

    def get_context_object_name(self, obj):
        return "streams"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Stream Schedule"
        in_dst = True  # False after Fall. Success after Spring.
        if in_dst:
            context["friday_time_utc"] = "01:00 UTC (Saturday)"
            context["sunday_time_utc"] = "19:00 UTC"
            context["monday_time_utc"] = "01:00 UTC (Tuesday)"
        else:
            context["friday_time_utc"] = "02:00 UTC (Saturday)"
            context["sunday_time_utc"] = "20:00 UTC"
            context["monday_time_utc"] = "02:00 UTC (Tuesday)"

        context["meta_tags"] = Meta_Tag_Block(url=self.request.get_full_path(), title=context["title"], description="Stream schedule for Worlds of ZZT on Twitch. Watch live at https://twitch.tv/worldsofzzt")
        return context
