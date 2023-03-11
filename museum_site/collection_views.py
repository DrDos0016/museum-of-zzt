from django.template.defaultfilters import slugify
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.shortcuts import render

from museum_site.constants import *
from museum_site.forms.collection_forms import Collection_Content_Form
from museum_site.models import *


class Collection_Create_View(CreateView):
    model = Collection
    template_name_suffix = "-form"
    fields = ["title", "short_description", "description", "visibility", "default_sort"]

    def setup(self, request, *args, **kwargs):
        super().setup(request, **kwargs)
        self.url_name = self.request.resolver_match.url_name
        self.get_page_title()

    def get_page_title(self):
        self.title = "Create New Collection"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["action"] = "Create"

        # Remove "Removed" from the visbility options
        context["form"].fields["visibility"].choices = context["form"].fields["visibility"].choices[1:]

        return context

    def form_valid(self, form):
        # Set user information
        form.instance.user = self.request.user

        # Check for a duplicate slug
        slug = slugify(self.request.POST.get("title"))
        if Collection.objects.duplicate_check(slug):
            form.add_error("title", "The requested collection title is already in use.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("manage_collection_contents", kwargs={"slug": self.object.slug})


class Collection_Update_View(UpdateView):
    model = Collection
    template_name_suffix = "-form"
    fields = ["title", "short_description", "description", "visibility", "default_sort"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        context["title"] = "Edit Collection"

        # Remove "Removed" from the visbility options
        context["form"].fields["visibility"].choices = context["form"].fields["visibility"].choices[1:]
        return context

    def form_valid(self, form):
        # Check for a duplicate slug in a collection that isn't this one
        slug = slugify(self.request.POST.get("title"))
        if Collection.objects.check_slug_overlap(self.object.pk, slug):
            form.add_error("title", "The requested collection title is already in use.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("my_collections")


class Collection_Delete_View(DeleteView):
    model = Collection
    template_name_suffix = "-form"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["action"] = "Delete"
        context["title"] = "Delete Collection"
        return context

    def get_success_url(self):
        return reverse("my_collections")


class Collection_Manage_Contents_View(FormView):
    form_class = Collection_Content_Form
    template_name = "museum_site/collection-manage-contents-form.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, **kwargs)
        self.collection_slug = self.request.resolver_match.kwargs["slug"]
        self.collection = Collection.objects.get(slug=self.collection_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Manage Collection Contents"
        context["operation"] = self.request.GET.get("operation", "add")

        context["collection_actions"] = [
            {"text": "Add To Collection", "url": "?operation=add", },
            {"text": "Remove From Collection", "url": "?operation=remove", },
            {"text": "Arrange Collection", "url": "?operation=arrange", },
            {"text": "Edit Collection Entry", "url": "?operation=edit-entry", }
        ]

        ops = {"add": 0, "remove": 1, "arrange": 2, "edit-entry": 3}
        operation_idx = ops[self.request.GET.get("operation", "add")]
        context["action"] = context["collection_actions"][operation_idx]

        context["form"].fields["collection_id"].initial = self.collection.id
        context["collection"] = self.collection
        context["contents"] = Collection_Entry.objects.get_items_in_collection(context["collection"])
        return context

    def form_valid(self, form):
        return "Ok!"


class On_The_Fly_Collections_View(TemplateView):
    template_name = "museum_site/collection-on-the-fly-collections.html"
    title = "Manage On The Fly Collections"

    def get(self, request, *args, **kwargs):
        context = {"title": self.title}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        request.session["active_tool"] = "on-the-fly-collections" if request.POST.get("on_the_fly") == "enable" else ""

        context = {"title": self.title}
        if request.session["active_tool"] == "on-the-fly-collections":
            context["output"] = "On The Fly Collections are now enabled."
            request.session["active_tool_template"] = "museum_site/tools/on-the-fly-collections.html"
        else:
            context["output"] = "On The Fly Collections are now disabled."
            request.session["active_tool_template"] = ""
        return render(request, self.template_name, context)
