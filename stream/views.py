from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

from museum_site.core.transforms import qs_manual_order
from museum_site.models import File
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
    else:
        today = datetime.now()
        stream = Stream.objects.filter(when__gte=today).first()
    context["stream"] = stream
    return render(request, "stream/overview.html", context)


@method_decorator(staff_member_required, name="dispatch")
class Stream_Create_View(CreateView):
    model = Stream
    fields = ["title", "description", "when", "preview_image", "entries"]
    template_name = "museum_site/generic-form-display-output.html"
    success_url = reverse_lazy("stream_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Stream"
        context["form"].heading = "Create Stream"
        context["form"].submit_value = "Create"
        context["form"].attrs = {"method": "POST", "action": self.success_url}
        context["form"].attrs = {"method": "POST"}
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


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
        return context


@method_decorator(staff_member_required, name="dispatch")
class Stream_Entry_Create_View(CreateView):
    model = Stream_Entry
    fields = ["zfile", "title_override", "author_override", "company_override", "release_date_override", "preview_image_override"]
    template_name = "museum_site/generic-form-display-output.html"
    success_url = reverse_lazy("stream_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Stream Entry"
        context["form"].heading = "Create Stream Entry"
        context["form"].submit_value = "Create"
        context["form"].attrs = {"method": "POST", "action": self.success_url}
        context["form"].attrs = {"method": "POST"}
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
