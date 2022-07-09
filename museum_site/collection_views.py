from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from museum_site.common import *
from museum_site.constants import *
from museum_site.forms import Collection_Content_Form
from museum_site.models import *
from museum_site.base_views import *


class Collection_Directory_View(Directory_View):
    model = Collection

    def setup(self, request, *args, **kwargs):
        super().setup(request, **kwargs)
        self.get_page_title()

    def get_page_title(self):
        if self.url_name == "my_collections":
            self.title = "My Collections"

    def get_queryset(self):
        if self.url_name == "my_collections":
            qs = Collection.objects.filter(user_id=self.request.user.id)
        else:  # Default listing
            qs = Collection.objects.filter(visibility=Collection.PUBLIC, item_count__gte=1)

        # Sorting
        qs = sort_qs(qs, self.request.GET.get("sort"), self.model.sort_keys, "-modified")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prefix_template"] = "museum_site/prefixes/collection.html"
        context["action"] = "Create"

        return context


class Collection_Detail_View(DetailView):
    model = Collection
    template_name = "museum_site/collection-view.html"
    error_template_name = "museum_site/collection-invalid-permissions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view"] = "detailed"

        if context["collection"].visibility == Collection.PRIVATE:
            if self.request.user.id != context["collection"].user_id:
                return {"forbidden": True}

        # Get the contents of this collection
        entries = Collection_Entry.objects.filter(collection=context["collection"])
        entries = sort_qs(entries, self.request.GET.get("sort"), Collection_Entry.sort_keys, "canonical")

        context["sort_options"] = Collection_Entry.sort_options
        context["page"] = entries
        return context

    def render_to_response(self, context, **kwargs):
        if context.get("forbidden"):
            self.template_name = self.error_template_name
        return super().render_to_response(context, **kwargs)


class Collection_Create_View(CreateView):
    model = Collection
    template_name_suffix = "-form"
    fields = ["title", "short_description", "description", "visibility"]

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
        if Collection.objects.filter(slug=slug).exists():
            form.add_error("title", "The requested collection title is already in use.")
            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse("manage_collection_contents", kwargs={"slug": self.object.slug})


class Collection_Update_View(UpdateView):
    model = Collection
    template_name_suffix = "-form"
    fields = ["title", "short_description", "description", "visibility"]

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
        if Collection.objects.exclude(pk=self.object.pk).filter(slug=slug).exists():
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
            {
                "text": "Add To Collection",
                "url": "?operation=add",

            },
            {
                "text": "Remove From Collection",
                "url": "?operation=remove",

            },
            {
                "text": "Arrange Collection",
                "url": "?operation=arrange",

            },
            {
                "text": "Edit Collection Entry",
                "url": "?operation=edit-entry",
            }
        ]
        context["action"] = context["collection_actions"][0]

        context["form"].fields["collection_id"].initial = self.collection.id
        context["collection"] = self.collection
        context["contents"] = Collection_Entry.objects.filter(collection=context["collection"])
        return context

    def form_valid(self, form):
        return "Ok!"
