from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from museum_site.common import *
from museum_site.constants import *
from museum_site.models import *
from museum_site.base_views import *


class Collection_Directory_View(Directory_View):
    model = Collection
    #category = "Collection"
    #template_name = "museum_site/generic-directory.html"
    #url_name = "browse_collections"
    #query_string = ""

    def setup(self, request, *args, **kwargs):
        super().setup(request, **kwargs)
        self.get_page_title()

        #if self.url_name == "user_collections"

    def get_page_title(self):
        if self.url_name == "my_collections":
            self.title = "My Collections"

    def get_queryset(self):
        if self.url_name == "my_collections":
            qs = Collection.objects.filter(user_id=self.request.user.id)
        else:  # Default listing
            qs = Collection.objects.filter(visibility=Collection.PUBLIC)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prefix_template"] = "museum_site/prefixes/collection.html"
        return context


class Collection_Detail_View(DetailView):
    model = Collection
    template_name = "museum_site/collection-view.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["view"] = "detailed"
        print("CONTEXT", context)

        items = context["collection"].contents.all()

        # Get the descriptions used for each item in the collection
        entries = Collection_Entry.objects.filter(collection=context["collection"])

        context["page"] = entries
        return context

class Collection_Create_View(CreateView):
    model = Collection
    template_name_suffix = "-form"
    fields= ["title", "short_description", "description", "visibility"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create New Collection"

        # Remove "Removed" from the visbility options
        context["form"].fields["visibility"].choices = context["form"].fields["visibility"].choices[1:]

        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("index")
