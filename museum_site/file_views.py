import os
import urllib.parse
import zipfile

from time import time

from django.core.cache import cache
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from museum_site.constants import *
from museum_site.core import *
from museum_site.core.detail_identifiers import *
from museum_site.core.redirects import explicit_redirect_check, redirect_with_querystring
from museum_site.forms.zfile_forms import Advanced_Search_Form
from museum_site.generic_model_views import Model_List_View, Model_Search_View
from museum_site.models import *
from museum_site.models import File as ZFile


@rusty_key_check
def file_attributes(request, key):
    data = {}
    data["file"] = get_object_or_404(File, key=key)
    data["reviews"] = Review.objects.for_zfile(data["file"].pk).defer("content")
    data["title"] = data["file"].title + " - Attributes"
    return render(request, "museum_site/attributes.html", data)


@rusty_key_check
def file_download(request, key):
    """ Returns page listing all download locations with a provided file """
    data = {}
    data["file"] = get_object_or_404(File, key=key)
    data["title"] = data["file"].title + " - Downloads"
    data["downloads"] = data["file"].downloads.all()
    data["letter"] = data["file"].letter
    return render(request, "museum_site/download.html", data)


@rusty_key_check
def file_viewer(request, key, local=False):
    """ Returns page exploring a file's zip contents """
    data = {
        "content_classes": ["fv-grid"],
        "details": [],
        "local": local,
        "files": [],
    }

    if not local:
        qs = File.objects.filter(key=key)
        if len(qs) == 1:
            data["file"] = qs[0]
        else:
            return redirect("/search?filename={}&err=404".format(key))

        # Check for explicit flag/permissions
        if data["file"].explicit:
            check = explicit_redirect_check(request, data["file"].pk)
            if check != "NO-REDIRECT":
                return check

        data["title"] = data["file"].title
        data["letter"] = data["file"].letter

        # Check for recommended custom charset
        for charset in cache.get("CUSTOM_CHARSETS", []):
            if data["file"].id == charset["id"]:
                data["custom_charset"] = charset["filename"]
                break

        if data["file"].is_detail(DETAIL_UPLOADED):
            letter = "uploaded"
            data["uploaded"] = True
        if data["file"].is_detail(DETAIL_WEAVE):
            data["weave"] = True

        zip_file = zipfile.ZipFile(data["file"].phys_path())
        files = zip_file.namelist()
        files.sort(key=str.lower)
        data["zip_info"] = sorted(zip_file.infolist(), key=lambda k: k.filename.lower())
        data["zip_comment"] = zip_file.comment.decode("latin-1")
        # TODO: "latin-1" may or may not actually be the case

        # Filter out directories (but not their contents)
        for f in files:
            if (f and f[-1] != os.sep and not f.startswith("__MACOSX" + os.sep) and not f.upper().endswith(".DS_STORE")):
                data["files"].append(f)
        data["load_file"] = urllib.parse.unquote(request.GET.get("file", ""))
        data["load_board"] = request.GET.get("board", "")
    else:  # Local files
        data["file"] = "Local File Viewer"
        data["letter"] = ""

    # Sort files into ZZT, Super ZZT, SAV, BRD, and non-ZZT extensions
    all_files = {"zzt": [], "szzt": [], "sav": [], "brd": [], "misc": []}
    keys = list(all_files.keys())
    for fname in data["files"]:
        ext = fname.split(".")[-1].lower()
        if ext in keys:
            all_files[ext].append(fname)
        else:
            all_files["misc"].append(fname)
    data["files"] = []
    for k in keys:
        sorted(all_files[k])
        data["files"] += all_files[k]

    data["charsets"] = []
    data["custom_charsets"] = []

    if not data["local"]:
        if data["file"].is_detail(DETAIL_ZZT):
            for charset in cache.get("CHARSETS", []):
                if charset["engine"] == "ZZT":
                    data["charsets"].append(charset)
            for charset in cache.get("CUSTOM_CHARSETS", []):
                if charset["engine"] == "ZZT":
                    data["custom_charsets"].append(charset)
        elif data["file"].is_detail(DETAIL_SZZT):
            for charset in cache.get("CHARSETS", []):
                if charset["engine"] == "SZZT":
                    data["charsets"].append(charset)
            for charset in cache.get("CUSTOM_CHARSETS", []):
                if charset["engine"] == "SZZT":
                    data["custom_charsets"].append(charset)
        else:
            data["charsets"] = cache.get("CHARSETS", [])
            data["custom_charsets"] = cache.get("CUSTOM_CHARSETS", [])
    # TODO LOCAL FILES SHOW ZZT AND SUPER ZZT CHARSETS
    else:
        data["charsets"] = cache.get("CHARSETS", [])
        data["custom_charsets"] = cache.get("CUSTOM_CHARSETS", [])

    return render(request, "museum_site/file.html", data)


def get_file_by_pk(request, pk):
    f = get_object_or_404(File, pk=pk)
    return redirect(f.attributes_url())


def advanced_search(request):
    """ Returns page containing multiple filters to use when searching ZFiles """
    data = {"title": "Advanced Search"}

    if request.GET:
        form = Advanced_Search_Form(request.GET)

        if request.GET.get("action") != "edit" and form.is_valid():
            return redirect_with_querystring("search", request.GET.urlencode())
    else:
        form = Advanced_Search_Form(initial={"details": [DETAIL_ZZT, DETAIL_SZZT, DETAIL_WEAVE, DETAIL_UPLOADED]})

    data["form"] = form
    return render(request, "museum_site/generic-form-display.html", data)


class ZFile_List_View(Model_List_View):
    model = ZFile
    letter = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.letter = self.kwargs.get("letter")
        self.search_type = None
        self.field = self.kwargs.get("field")
        self.value = self.kwargs.get("value")
        self.author = None
        self.company = None
        self.detail = None
        self.genre = None

        if request.path == "/file/search/":
            self.search_type = "basic" if request.GET.get("q") else "advanced"

        # Default sort based on path
        if self.sorted_by is None:
            if request.path == "/file/browse/":
                self.sorted_by = "-publish_date"
            if request.path == "/file/browse/detail/uploaded/":
                self.sorted_by = "uploaded"
            if request.path == "/file/roulette/":
                self.sorted_by = "random"

    def get_queryset(self):
        qs = ZFile.objects.search(self.request.GET)

        if self.letter:
            qs = qs.filter(letter=self.letter)
        elif self.request.path == "/file/browse/new-finds/":
            qs = ZFile.objects.new_finds()
        elif self.request.path == "/file/browse/new-releases/":
            qs = ZFile.objects.new_releases()
        elif self.request.path == "/file/roulette/":
            qs = ZFile.objects.roulette(self.request.GET["seed"], PAGE_SIZE)  # Cap results for list view
        elif self.search_type == "advanced":
            cleaned_params = clean_params(self.request.GET.copy(), list_items=["details"])
            qs = ZFile.objects.advanced_search(cleaned_params)
        elif self.value and self.field == "author":
            qs = qs.filter(authors__slug=self.value)
            self.author = Author.objects.reach(slug=self.value)
        elif self.value and self.field == "company":
            qs = qs.filter(companies__slug=self.value)
            self.company = Company.objects.reach(slug=self.value)
        elif self.value and self.field == "detail":
            qs = qs.filter(details__slug=self.value)
            self.detail = Detail.objects.reach(slug=self.value)
        elif self.value and self.field == "genre":
            qs = qs.filter(genres__slug=self.value)
            self.genre = Genre.objects.reach(slug=self.value)
        elif self.value and self.field == "year":
            if self.value == "unk":
                qs = qs.filter(release_date=None)
            else:
                qs = qs.filter(release_date__gte="{}-01-01".format(self.value), release_date__lte="{}-12-31".format(self.value))
        elif self.value and self.field == "language":
            qs = qs.filter(language__icontains=self.value)

        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_type"] = self.search_type

        # Modify sort options based on path
        if self.request.path == "/file/browse/":
            context["sort_options"] = [{"text": "Publish Date", "val": "-publish_date"}] + context["sort_options"]
        elif self.request.path == "/file/browse/new-finds/":
            context["sort_options"] = None
            context["sort"] = "-publish_date"
        elif self.request.path == "/file/browse/new-releases/":
            context["sort_options"] = None
            context["prefix_template"] = "museum_site/prefixes/new-releases.html"
        elif self.request.path == "/file/browse/detail/uploaded/":
            context["sort_options"] = [{"text": "Upload Date", "val": "uploaded"}] + context["sort_options"]
        elif self.request.path == "/file/roulette/":
            context["sort_options"] = [{"text": "Random", "val": "random"}] + context["sort_options"]

        # Setup prefix text/template
        if self.detail:
            context["prefix_text"] = self.detail.description
        if self.genre:
            context["prefix_text"] = self.genre.description
        if self.request.path == "/file/browse/new-finds/":
            context["prefix_template"] = "museum_site/prefixes/new-finds.html"
        if self.request.path == "/file/roulette/":
            context["prefix_template"] = "museum_site/prefixes/roulette.html"
        if self.request.GET.get("err") == "404":
            context["prefix_template"] = "museum_site/prefixes/file-404.html"

        # Debug cheat
        if self.request.GET.get("q") == "+DEBUG":
            self.request.session["DEBUG"] = 1
        elif self.request.GET.get("q") == "-DEBUG":
            del self.request.session["DEBUG"]

        # Add basic search filters
        if self.search_type == "basic":
            context["basic_search_fields"] = ["Title", "Author", "Company", "Genre", "Filename"]

        # Add search modify button
        context["query_edit_url_name"] = "search"

        # Remove view/sort widgets if no results were found
        if not context.get("object_list"):
            context["sort_options"] = None
            context["available_views"] = []

        return context

    def get_title(self):
        if self.letter:
            return "Browse - {}".format(self.letter.upper())
        elif self.genre:
            return "Browse Genre - {}".format(self.genre.title)
        elif self.detail:
            if self.detail.title == "Uploaded":
                return "Upload Queue"
            elif self.detail.title == "Featured World":
                return "Featured Worlds"
            return "Browse Detail - {}".format(self.detail.title)
        elif self.request.path == "/file/browse/new-finds/":
            return "New Finds"
        elif self.request.path == "/file/browse/new-releases/":
            return "New Releases"
        elif self.request.path == "/file/roulette/":
            return "Roulette"
        elif self.request.path == "/file/search/":
            title = 'Search Results - "{}"' .format(self.request.GET.get("q", ""))
            if self.request.GET.get("err") == "404":
                return "Automatic Search Results"
            elif self.search_type == "advanced":
                return "Search Results"
            return title
        elif self.request.path.startswith("/file/browse/author/") and self.author:
            return "Browse Author - {}".format(self.author.title)
        elif self.request.path.startswith("/file/browse/company/") and self.company:
            return "Browse Company - {}".format(self.company.title)
        elif self.request.path.startswith("/file/browse/genre/") and self.genre:
            return "Browse Genre - {}".format(self.genre.title)
        elif self.request.path.startswith("/file/browse/detail/") and self.detail:
            return "Browse Detail - {}".format(self.detail.title)
        elif self.request.path.startswith("/file/browse/year/"):
            return "Browse Year - {}".format(self.value)
        elif self.request.path.startswith("/file/browse/language/"):
            return "Browse Language - {}".format(self.value.upper())
        # Default
        return "Browse - All Files"



class ZFile_Search_View(Model_Search_View):
    form_class = Advanced_Search_Form
    model = File
    model_list_view_class = ZFile_List_View
    template_name = "museum_site/generic-form-display.html"
    title = "File Search"


class ZFile_Article_List_View(Model_List_View):
    model = Article

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if self.sorted_by is None:
            self.sorted_by = "title"

    def get_queryset(self):
        key = self.kwargs.get("key")
        self.head_object = ZFile.objects.get(key=key)
        qs = Article.objects.accessible().filter(file=self.head_object)
        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["file"] = self.head_object
        context["head_object"] = None
        context["title"] = "{} - Articles".format(self.head_object.title)
        context["header_idx"] = 2
        return context


class ZFile_Review_List_View(Model_List_View):
    model = Review
    template_name = "museum_site/file-review.html"
    allow_pagination = False

    def get_queryset(self):
        key = self.kwargs.get("key")
        if key.lower().endswith(".zip"):
            key = key[:-4]
        self.head_object = ZFile.objects.get(key=key)
        qs = Review.objects.for_zfile_and_user(pk=self.head_object.pk, ip=self.request.META[REMOTE_ADDR_HEADER], user_id=self.request.user.id)
        self.qs = qs  # Needed to easily check for recent reviews later
        qs = self.sort_queryset(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["file"] = self.head_object
        context["title"] = "{} - Reviews".format(self.head_object.title)
        context["today"] = datetime.now(tz=timezone.utc)
        context["sort_options"] = [
            {"text": "Newest", "val": "-date"},
            {"text": "Oldest", "val": "date"},
            {"text": "Rating", "val": "rating"}
        ]

        # Check that the file supports reviews
        if not context["file"].can_review:
            context["cant_review_message"] = "This file is no longer accepting new reviews at this time."
            return context

        # Check for banned users
        if banned_ip(self.request.META[REMOTE_ADDR_HEADER]):
            context["cant_review_message"] = "<b>Banned account.</b>"
            return context

        # Prevent doubling up on reviews
        cutoff = context["today"] + timedelta(days=-1)
        recent = self.qs.filter(ip=self.request.META.get(REMOTE_ADDR_HEADER), date__gte=cutoff)
        if recent:
            context["cant_review_message"] = (
                "<i>You have <a href='#rev-{}'>recently reviewed</a> this file and cannot submit an additional review at this time.</i>".format(
                    recent.first().pk
                )
            )
            return context

        # Prevent unpublished/lost file reviews
        if context["file"].is_detail(DETAIL_UPLOADED):
            context["cant_review_message"] = "Unpublished files cannot be reviewed as their content may still be modified by the uploader."
            return context
        elif context["file"].is_detail(DETAIL_LOST):
            context["cant_review_message"] = "Lost files cannot be reviewed as they cannot be played!"
            return context

        # Initialize form
        review_form = Review_Form(self.request.POST) if self.request.POST else Review_Form()

        # Remove anonymous option for logged in users
        if self.request.user.is_authenticated:
            del review_form.fields["author"]

        # Post a review if one was submitted
        if self.request.POST and review_form.is_valid() and not recent:
            review = review_form.save(commit=False)
            if self.request.user.is_authenticated:
                review.author = self.request.user.username
                review.user_id = self.request.user.id
            review.ip = self.request.META.get(REMOTE_ADDR_HEADER)
            review.date = context["today"]
            review.zfile_id = self.head_object.id

            # Simple spam protection
            if self.head_object.can_review == File.REVIEW_APPROVAL or (review.content.find("href") != -1) or (review.content.find("[url=") != -1):
                review.approved = False
            if not self.request.user.is_authenticated and review.content.find("http") != -1:
                review_approved = False
            review.save()

            # Update file's review count/scores if the review is approved
            if self.head_object.can_review == ZFile.REVIEW_YES and review.approved:
                self.head_object.calculate_reviews()
                # Make Announcement
                discord_announce_review(review)
                self.head_object.save()

            # Re-get the queryset with the new review included and without including the form again
            context["object_list"] = self.get_queryset()
            context["recent"] = review.pk
            return context

        context["form"] = review_form
        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


def prepare_roulette(request):
    """ Ensure a seed is provided to use for the roulette """
    if request.GET.get("seed"):
        return ZFile_List_View.as_view()(request)
    else:
        return redirect(reverse("roulette") + "?seed={}".format(int(time())))
