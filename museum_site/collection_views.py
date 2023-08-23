from django.template.defaultfilters import slugify
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.shortcuts import render

from museum_site.constants import *
from museum_site.forms.collection_forms import Collection_Content_Form
from museum_site.generic_model_views import Model_List_View
from museum_site.models import *
from museum_site.templatetags.site_tags import render_markdown


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
        return reverse("collection_manage_contents", kwargs={"slug": self.object.slug})


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
        return reverse("collection_user")


class Collection_Delete_View(DeleteView):
    model = Collection
    template_name_suffix = "-form"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["action"] = "Delete"
        context["title"] = "Delete Collection"
        return context

    def get_success_url(self):
        return reverse("collection_user")


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
        context = {"title": self.title}
        if request.POST.get("on_the_fly") == "enable":
            context["output"] = "On The Fly Collections are now enabled."
            request.session["active_tool"] = "on-the-fly-collections"
            request.session["active_tool_template"] = "museum_site/tools/on-the-fly-collections.html"
            request.session["otf_refresh"] = True
        else:
            if request.session.get("active_tool") == "on-the-fly-collections":
                request.session["active_tool"] = ""
            context["output"] = "On The Fly Collections are now disabled."
            request.session["active_tool_template"] = ""
        return render(request, self.template_name, context)


class Collection_List_View(Model_List_View):
    model = Collection

    def get_queryset(self):
        if self.request.path == "/collection/user/":
            qs = Collection.objects.collections_for_user(self.request.user.id)
        else:  # Default listing
            qs = Collection.objects.populated_public_collections()

        if self.sorted_by is None:
            self.sorted_by = "-modified"

        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prefix_template"] = "museum_site/prefixes/collection.html"
        return context

    def get_title(self):
        if self.request.path == "/collection/user/":
            return "My Collections"
        return super().get_title()


class Collection_Contents_View(Model_List_View):
    model = Collection_Entry

    def get_queryset(self):
        slug = self.kwargs.get("collection_slug")
        self.head_object = Collection.objects.get(slug=slug)
        qs = Collection_Entry.objects.get_items_in_collection(self.head_object.pk)

        if self.sorted_by is None:
            self.sorted_by = self.head_object.default_sort

        qs = self.sort_queryset(qs)
        # Remove duplicate entries -- TODO This seems quite janky
        if self.sorted_by in ["author", "company"]:
            pruned = []
            observed_ids = []
            for i in qs:
                if i.pk not in observed_ids:
                    observed_ids.append(i.pk)
                    pruned.append(i)
            return pruned

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.head_object.title
        context["prefix_text"] = "{}\n<h2>Collection Contents ({} file{})</h2>".format(
            render_markdown(self.head_object.description),
            self.head_object.item_count,
            ("" if self.head_object.item_count == 1 else "s")
        )

        # If there's no manual order available, don't show the option
        if context["head_object"].default_sort != "manual":
            context["sort_options"] = Collection_Entry.sort_options[1:]

        return context

    def render_to_response(self, context, **kwargs):
        # Prevent non-creators from viewing private collections
        if context["head_object"].visibility == Collection.PRIVATE:
            if self.request.user.id != context["head_object"].user_id:
                self.template_name = "museum_site/collection-invalid-permissions.html"
        return super().render_to_response(context, **kwargs)
