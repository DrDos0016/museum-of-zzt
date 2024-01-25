import math
import re

from django.http import HttpResponseForbidden
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import ListView

from museum_site.constants import *
from museum_site.core.model_utils import delete_feedback
from museum_site.forms.review_forms import Review_Search_Form, Feedback_Delete_Confirmation_Form, Review_Form, Feedback_Edit_Form
from museum_site.generic_model_views import Model_Search_View, Model_List_View
from museum_site.models import *


class Reviewer_Directory_View(ListView):
    model = Review
    title = "Reviewer Directory"
    category = "Reviewer"
    template_name = "museum_site/generic-listing.html"
    url_name = "review_browse_author"
    query_string = ""

    def get_queryset(self):
        qs = Review.objects.reviewer_directory()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["url_name"] = self.url_name
        context["query_string"] = self.query_string
        context["items"] = []

        # Break the list of results into 4 columns
        db_author_list = sorted(self.object_list, key=lambda s: re.sub(r'(\W|_)', "é", s.lower()))

        for entry in db_author_list:
            item = {"name": entry, "letter": ""}
            if entry[0] in "1234567890":
                item["letter"] = "#"
            elif entry[0].upper() not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                item["letter"] = "*"
            else:
                item["letter"] = entry[0].upper()

            context["items"].append(item)

        context["split"] = math.ceil(len(context["items"]) / 4.0)
        return context


class Review_List_View(Model_List_View):
    model = Review

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.sorted_by is None:
            self.sorted_by = "-date"
        self.author = self.kwargs.get("author")

    def get_title(self):
        if self.request.GET:
            difference = 0
            difference = difference - 1 if self.request.GET.get("page") else difference
            difference = difference - 1 if self.request.GET.get("sort") else difference
            difference = difference - 1 if self.request.GET.get("view") else difference
            print("LEN  IS", len(self.request.GET.keys()))
            print("DIFF IS", difference)
            if (len(self.request.GET.keys()) + difference) > 0:
                return "Search Results"
            else:
                return super().get_title()
        else:
            return super().get_title()

    def get_queryset(self):
        if self.author:
            qs = Review.objects.search(p={"author": self.author, "non_search": True})
        else:
            qs = Review.objects.search(self.request.GET)

        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO This should still be the case, but it's causing an error on the live site right now
        #if self.author:  # Don't allow sorting by reviewer when showing a single reviewer's reviews
        #    context["sort_options"].remove({"text": "Author", "val": "reviewer"})

        if self.request.GET:
            context["search_type"] = "Advanced"
            context["query_edit_url_name"] = "review_search"

        if self.request.path == "/review/browse/":
            context["rss_info"] = {"url_name": "rss_reviews"}
        return context


class Feedback_Search_View(Model_Search_View):
    form_class = Review_Search_Form
    model = Review
    model_list_view_class = Review_List_View
    template_name = "museum_site/generic-form-display.html"
    title = "Feedback Search"


class Feedback_Delete_Confirmation_View(FormView):
    form_class = Feedback_Delete_Confirmation_Form
    template_name = "museum_site/feedback-delete.html"
    feedback = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.feedback = Review.objects.filter(pk=request.GET.get("pk")).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.feedback:
            context["selected_zfile"] = self.feedback.zfile
            context["selected_feedback"] = self.feedback
            context["form"].fields["zfile_key"].widget.attrs["value"] = self.feedback.zfile.key

        if self.request.GET.get("success"):
            context["heading"] = "Feedback Deleted Successfully!!"
            context["testing"] = self.testing
            context["selected_zfile"] = File.objects.filter(pk=self.request.POST.get("zfile_id")).first()
        else:
            context["heading"] = "Confirm Deletion"
        return context

    def form_valid(self, form):
        # Verify the feedback is yours to delete
        self.feedback.request = self.request
        self.feedback._init_yours()
        if self.feedback.is_yours:
            delete_feedback(self.feedback)

        #  Redirect to file's feedback page
        self.success_url = File.objects.get(key=self.request.POST["zfile_key"]).review_url()
        return super().form_valid(form)



class Feedback_Edit_View(FormView):
    """ TODO: This one seems weirdly hacked together """
    form_class = Feedback_Edit_Form
    template_name = "museum_site/feedback-edit.html"
    feedback = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.feedback = Review.objects.filter(pk=kwargs.get("pk")).first()
        self.initial={
            "title": self.feedback.title, "content": self.feedback.content, "rating": self.feedback.rating, "spotlight": 1,
            "tags": self.feedback.tags.all(), "zfile_id": self.feedback.zfile_id
        }
        self.success_url = self.feedback.get_absolute_url()

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated and self.request.user.pk == self.feedback.user_id:
            return super().get(*args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_form(self):
        form =  super().get_form()
        del form.fields["author"]
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.feedback:
            context["selected_zfile"] = self.feedback.zfile
            context["selected_feedback"] = self.feedback
        else:
            context["heading"] = "Edit Feedback"

        return context

    def form_valid(self, form):
        if self.request.user.is_authenticated and self.request.user.pk == self.feedback.user_id:
            form.process(self.request, self.feedback.zfile, self.feedback)
        else:
            return HttpResponseForbidden()

        return super().form_valid(form)
