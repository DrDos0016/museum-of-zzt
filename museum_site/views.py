from django.shortcuts import render
from .common import *

def advanced_search(request):
    """ Returns page containing multiple filters to use when searching """
    data = {
        "title": "Advanced Search",
        "mode": "search",
        "genres": GENRE_LIST,
        "years": [str(x) for x in range(1991, YEAR + 1)]
    }

    data["details_list"] = request.GET.getlist("details", ADV_SEARCH_DEFAULTS)
    return render(request, "museum_site/advanced_search.html", data)


def article(request, letter, filename):
    """ Returns page listing all articles associated with a provided file.
    If there is just one article, display it instead.
    """
    data = {}
    data["file"] = File.objects.filter(letter=letter, filename=filename)
    if len(data["file"]) == 0:
        raise Http404()
    elif len(data["file"]) > 1:
        for file in data["file"]:
            if file.filename == filename:
                data["file"] = file
                break
    else:
        data["file"] = data["file"][0]
    data["title"] = data["file"].title + " - Articles"
    data["articles"] = data["file"].articles.all()
    data["letter"] = letter

    return render(request, "museum_site/article.html", data)


def article_directory(request, category="all"):
    """ Returns page listing all articles sorted either by date or name """
    data = {"title": "Article Dirctory"}
    data["sort"] = request.GET.get("sort", "category")
    if request.GET.get("sort") == "date":
        data["articles"] = Article.objects.defer(
            "content", "css"
        ).filter(published=True, parent=None).order_by("-date", "title")
    else:
        data["articles"] = Article.objects.defer(
            "content", "css"
        ).filter(published=True, parent=None).order_by("category", "title")

    if category != "all":
        data["articles"] = data["articles"].filter(
            category=category.replace("-", " ").title()
        )
    return render(request, "museum_site/article_directory.html", data)


def article_view(request, id, page=0):
    """ Returns an article pulled from the database """
    slug = request.path.split("/")[-1]
    page = int(page)
    id = int(id)
    data = {"id": id}

    data["article"] = get_object_or_404(Article, pk=id, published=True)
    data["page"] = page
    data["page_count"] = data["article"].content.count("<!--Page-->") + 1
    data["page_range"] = list(range(1, data["page_count"] + 1))
    data["next"] = None if page + 1 > data["page_count"] else page + 1
    data["prev"] = page - 1
    data["slug"] = str(slug)

    data["title"] = data["article"].title

    file = data["article"].file_set.all()
    if file:
        # TODO: Handle an article w/ multiple files (ex Zem + Zem 2)
        data["file"] = file[0]

    # Split article to current page
    data["article"].content = data["article"].content.split("<!--Page-->")[data["page"]-1]
    return render(request, "museum_site/article_view.html", data)


def browse(request, letter=None, details=[DETAIL_ZZT], page=1, show_description=False):
    """ Returns page containing a list of files filtered by letter, details,
    and page

    Keyword arguments:
    letter      -- The letter to filter by, may be a-z or 1. Default 'a'
    details     -- List of Details of files to filter by.
    page        -- Page of results to slice to. Default '1'
    show_description -- Shows the description field. Default False
    """
    data = {
        "mode": "browse",
        "details": details,
        "show_description": show_description
    }

    if letter is not None:
        data["title"] = "Browse - " + letter.upper()
    elif len(details) == 1:
        data["title"] = "Browse - " + CATEGORY_LIST[details[0]][1]
    else:
        data["title"] = "Browse"

    # Determine the viewing method
    data["view"] = get_view_format(request)

    sort = SORT_CODES[request.GET.get("sort", "title").strip()]

    # Handle "new additions"
    if request.path == "/new":
        sort = SORT_CODES["published"]

    # Query strings
    data["qs_sans_page"] = qs_sans(request.GET, "page")
    data["qs_sans_view"] = qs_sans(request.GET, "view")

    if data["view"] == "list":  # List gets a full listing on one page
        data["letter"] = letter if letter != "1" else "#"
        data["files"] = File.objects.filter(details__id__in=details)
        if letter:
            data["files"] = data["files"].filter(letter=letter)
        data["files"] = data["files"].order_by(*sort)
    else:  # Others list over multiple pages
        data["page"] = int(request.GET.get("page", page))
        data["letter"] = letter if letter != "1" else "#"
        data["files"] = File.objects.filter(details__id__in=details)
        if letter:
            data["files"] = data["files"].filter(letter=letter)
        data["files"] = data["files"].order_by(*sort)[
            (data["page"] - 1) * PAGE_SIZE:data["page"] * PAGE_SIZE
        ]
        data["count"] = File.objects.filter(details__id__in=details)
        if letter:
            data["count"] = data["count"].filter(letter=letter)
        data["count"] = data["count"].count()
        data["pages"] = int(math.ceil(1.0 * data["count"] / PAGE_SIZE))
        data["page_range"] = range(1, data["pages"] + 1)
        data["prev"] = max(1, data["page"] - 1)
        data["next"] = min(data["pages"], data["page"] + 1)

    # Show descriptions for lost worlds
    if DETAIL_LOST in details:
        data["show_description"] = True

    if DETAIL_UPLOADED in details:
        for file in data["files"]:
            file.letter = "uploaded"

    # Determine destination template
    if data["view"] == "list":
        destination = "museum_site/browse_list.html"
    elif data["view"] == "gallery":
        destination = "museum_site/browse_gallery.html"
    else:  # Detailed
        destination = "museum_site/browse.html"

    response = render(request, destination, data)

    # Set page view cookie
    response.set_cookie("view", data["view"], expires=datetime(3000, 12, 31))

    return response


def closer_look(request):
    """ Returns a listing of all Closer Look articles """
    data = {"title": "Closer Looks"}
    data["articles"] = Article.objects.filter(
        category="Closer Look", published=1, page=1
    )
    sort = request.GET.get("sort", "date")
    if sort == "title":
        data["articles"] = data["articles"].order_by("title")
    elif sort == "date":
        data["articles"] = data["articles"].order_by("-date")

    data["sort"] = sort
    data["page"] = int(request.GET.get("page", 1))
    data["articles"] = data["articles"][
        (data["page"] - 1) * PAGE_SIZE:data["page"] * PAGE_SIZE
    ]
    data["count"] = Article.objects.filter(category="Closer Look", published=1,
                                           page=1).count()
    data["pages"] = int(math.ceil(1.0 * data["count"] / PAGE_SIZE))
    data["page_range"] = range(1, data["pages"] + 1)
    data["prev"] = max(1, data["page"] - 1)
    data["next"] = min(data["pages"], data["page"] + 1)
    data["qs_sans_page"] = qs_sans(request.GET, "page")

    return render(request, "museum_site/closer_look.html", data)


def directory(request, category):
    """ Returns a directory of all authors/companies/genres in the database """
    data = {}
    data["category"] = category

    """ This can possibly be cached in some way, it's not going to change
    often.
    """
    data_list = []
    if category == "company":
        data["title"] = "Companies"
        companies = File.objects.values(
            "company"
        ).exclude(
            company=None
        ).exclude(
            company=""
        ).distinct().order_by("company")
        for c in companies:
            split = c["company"].split("/")
            for credited in split:
                if credited not in data_list:
                    data_list.append(credited)
    elif category == "author":
        data["title"] = "Authors"
        authors = File.objects.values("author").distinct().order_by("author")
        for a in authors:
            split = a["author"].split("/")
            for credited in split:
                if credited not in data_list:
                    data_list.append(credited)
    elif category == "genre":
        data["title"] = "Genres"
        # genres = File.objects.values("genre").distinct().order_by("genre")
        data_list = GENRE_LIST

    # Break the list of results into 4 columns
    data_list = sorted(data_list, key=lambda s: s.lower())

    data["list"] = data_list
    data["split"] = math.ceil(len(data["list"]) / 4.0)
    return render(request, "museum_site/directory.html", data)


def featured_games(request, page=1):
    """ Returns a page listing all games marked as Featured """
    data = {"title": "Featured Games"}
    data["no_list"] = True
    data["page"] = int(request.GET.get("page", page))
    featured = Detail.objects.get(pk=DETAIL_FEATURED)

    sort = SORT_CODES[request.GET.get("sort", "title").strip()]
    # Query strings
    data["qs_sans_page"] = qs_sans(request.GET, "page")
    data["qs_sans_view"] = qs_sans(request.GET, "view")

    data["featured"] = featured.file_set.all().order_by(
        *sort
    ).prefetch_related("articles").defer(
        "articles__content"
    )[(data["page"] - 1) * PAGE_SIZE:data["page"] * PAGE_SIZE]
    data["count"] = featured.file_set.all().count()
    data["pages"] = int(math.ceil(1.0 * data["count"] / PAGE_SIZE))
    data["page_range"] = range(1, data["pages"] + 1)
    data["prev"] = max(1, data["page"] - 1)
    data["next"] = min(data["pages"], data["page"] + 1)
    data["show_description"] = True
    data["show_featured"] = True

    return render(request, "museum_site/featured_games.html", data)


def file(request, letter, filename, local=False):
    """ Returns page exploring a file's zip contents """
    data = {}
    data["year"] = YEAR
    data["details"] = []  # Required to show all download links
    data["file"] = File.objects.filter(letter=letter, filename=filename)
    data["local"] = local
    if not local:
        if len(data["file"]) == 0:
            # Check if there's a matching zip with a different letter
            alternative = File.objects.filter(filename=filename)
            alt_count = alternative.count()
            if alt_count:
                if alt_count == 1:
                    response = redirect("file", letter=alternative[0].letter,
                                        filename=filename)
                    return response
                else:
                    response = redirect("search")
                    response['Location'] += "?filename=" + filename
                    return response
            raise Http404()
        elif len(data["file"]) > 1:
            for file in data["file"]:
                if file.filename == filename:
                    data["file"] = file
                    break
        else:
            data["file"] = data["file"][0]

        data["title"] = data["file"].title
        data["letter"] = letter

        if data["file"].is_uploaded():
            letter = "uploaded"
            data["uploaded"] = True
        zip = zipfile.ZipFile(os.path.join(SITE_ROOT, "zgames", letter, filename))
        files = zip.namelist()
        files.sort(key=str.lower)
        data["files"] = []
        # Filter out directories (but not their contents)
        for f in files:
            if f and f[-1] != os.sep:
                data["files"].append(f)
        data["load_file"] = request.GET.get("file", "")
        data["load_board"] = request.GET.get("board", "")
    else: # Local files
        data["file"] = "Local File Viewer"
        data["letter"] = letter

    data["charsets"] = CHARSET_LIST
    data["custom_charsets"] = CUSTOM_CHARSET_LIST


    return render(request, "museum_site/file.html", data)


def generic(request, title="", template=""):
    data = {"title": title}
    return render(request, "museum_site/"+ template + ".html")


def index(request):
    """ Returns front page """
    data = {}

    # Obtain latest content
    data["articles"] = Article.objects.all().order_by("-id")[:10]
    data["files"] = File.objects.all().exclude(details__id__in=[18]).order_by("-publish_date", "-id")[:10]  # TODO: Unhardcode
    data["reviews"] = Review.objects.all().order_by("-id")[:10]

    return render(request, "museum_site/index.html", data)


def local(request):
    """ Returns ZZT file viewer intended for local files """
    data = {}
    data["charsets"] = CHARSET_LIST
    data["custom_charsets"] = CUSTOM_CHARSET_LIST
    return render(request, "museum_site/local_file.html", data)


def mass_downloads(request):
    """ Returns a page for downloading files by release year """
    data = {"title": "Mass Downloads"}
    # Read the json
    return render(request, "museum_site/mass_downloads.html", data)

def patron_plans(request):
    """ Redirects to the Patron only Google Doc for Closer Looks """
    data = {}

    # Ugh I have to keep the URL outside of my public repo...
    with open("/var/projects/museum/patron_plans.txt") as fh:
        url = fh.readline().strip()
        passphrase = fh.readline().strip()

    if request.POST.get("secret") == passphrase:
        return redirect(url)
    else:
        if request.POST.get("secret"):
            data["wrong_password"] = True
        return render(request, "museum_site/patreon_plans.html", data)


def play(request, letter, filename):
    """ Returns page to play file in the browser """
    data = {}
    data["file"] = File.objects.filter(letter=letter, filename=filename)
    if len(data["file"]) == 0:
        raise Http404()
    elif len(data["file"]) > 1:
        for file in data["file"]:
            if file.filename == filename:
                data["file"] = file
                break
    else:
        data["file"] = data["file"][0]
    data["title"] = data["file"].title + " - Play Online"
    data["letter"] = letter

    # Select a play method
    player_names = PLAY_METHODS.keys()
    player_names = ["archive"] # TODO: THIS IS A DEBUG UNTIL CERULEAN IS LIVE ON PRODUCTION

    player = request.GET.get("player")
    if player is None or player not in player_names:
        # If no player was provided, check for a cookie preference
        preferred_player = request.COOKIES.get("preferred_player", "")
        if preferred_player not in player_names:
            player = "archive"  # Default player
        else:
            player = preferred_player

    # Check player compatibility
    cookie_preferred = player  # In case the user's choice isn't available
    data["fallback"] = False

    if player == "cerulean":
        if not data["file"].supports_cerulean_player:
            player = "archive"
            data["fallback"] = True
    elif player == "archive":
        if not data["file"].archive_name:
            player = "cerulean"
            data["fallback"] = True

    # The player the page will use
    data["player"] = player
    data["players"] = PLAY_METHODS

    if data["file"].id in CUSTOM_CHARSET_MAP:
        data["custom_charset"] = CUSTOM_CHARSET_MAP[data["file"].id]
    else:
        data["custom_charset"] = None

    response = render(request, "museum_site/play.html", data)
    response.set_cookie("preferred_player", cookie_preferred, expires=datetime(3000, 12, 31))
    return response


def random(request):
    """ Returns a random ZZT file page """
    max_pk = File.objects.all().order_by("-id")[0].id

    file = None
    while not file:
        id = randint(1, max_pk)
        file = File.objects.filter(pk=id, details__id=DETAIL_ZZT)
        if file:
            file = file[0]

    return redirect("file/" + file.letter + "/" + file.filename)

def redir(request, url):
    return redirect(url, permanent=True)


def register(request):
    data = {}
    return render(request, "museum_site/register.html", data)


def review(request, letter, filename):
    """ Returns a page of reviews for a file. Handles POSTing new reviews """
    data = {}
    data["file"] = File.objects.filter(letter=letter, filename=filename)
    if len(data["file"]) == 0:
        raise Http404()
    elif len(data["file"]) > 1:
        for file in data["file"]:
            if file.filename == filename:
                data["file"] = file
                break
    else:
        data["file"] = data["file"][0]
    data["letter"] = letter
    data["title"] = data["file"].title + " - Reviews"

    # POST review
    if request.POST.get("action") == "post-review":
        review = Review()
        created = review.from_request(request)
        if created:
            review.full_clean()
            review.save()

        # Update file's review count/scores
        data["file"].recalculate_reviews()
        data["file"].save()

    data["reviews"] = Review.objects.filter(file_id=data["file"].id)
    return render(request, "museum_site/review.html", data)


def search(request):
    """ Searches database files. Returns the browse page filtered
        appropriately.
    """
    data = {"mode": "search", "title": "Search"}
    data["page"] = int(request.GET.get("page", 1))

    # Query strings
    data["qs_sans_page"] = qs_sans(request.GET, "page")
    data["qs_sans_view"] = qs_sans(request.GET, "view")
    sort = SORT_CODES[request.GET.get("sort", "title").strip()]

    # Determine the viewing method
    data["view"] = get_view_format(request)

    if request.GET.get("q"):  # Basic Search
        q = request.GET["q"].strip()
        data["q"] = request.GET["q"]
        qs = File.objects.filter(
            Q(title__icontains=q) |
            Q(aliases__alias__icontains=q) |
            Q(author__icontains=q) |
            Q(filename__icontains=q) |
            Q(company__icontains=q)
        ).exclude(details__id__in=[18])  # TODO: Unhardcode

        # Debug override
        if DEBUG:
            if request.GET.get("q") == "debug=blank":
                qs = File.objects.filter(screenshot="").exclude(details__id__in=[DETAIL_LOST])
            elif request.GET.get("q").startswith("debug="):
                ids = request.GET.get("q").split("=", maxsplit=1)[-1]
                qs = File.objects.filter(id__in=ids.split(",")).order_by("id")


        if data["view"] == "list":
            page_size = LIST_PAGE_SIZE
        else:
            page_size = PAGE_SIZE

        data["files"] = qs.order_by(
            *sort
        )[(data["page"] - 1) * page_size:data["page"] * page_size]
        data["count"] = qs.count()
        data["pages"] = int(1.0 * math.ceil(data["count"] / page_size))
        data["page_range"] = range(1, data["pages"] + 1)
        data["prev"] = max(1, data["page"] - 1)
        data["next"] = min(data["pages"], data["page"] + 1)

        if data["view"] == "gallery":
            destination = "museum_site/browse_gallery.html"
        elif data["view"] == "list":
            destination = "museum_site/browse_list.html"
        else:
            destination = "museum_site/browse.html"
    else:  # Advanced Search
        data["advanced_search"] = True
        qs = File.objects.all()
        if request.GET.get("title", "").strip():
            qs = qs.filter(
                title__icontains=request.GET.get("title", "").strip()
            )
        if request.GET.get("author", "").strip():
            qs = qs.filter(
                author__icontains=request.GET.get("author", "").strip()
            )
        if request.GET.get("filename", "").strip():
            qs = qs.filter(
                filename__icontains=request.GET.get(
                    "filename", ""
                ).replace(
                    ".zip", ""
                ).strip()
            )
        if request.GET.get("company", "").strip():
            qs = qs.filter(
                company__icontains=request.GET.get("company", "").strip()
            )
        if (request.GET.get("genre", "").strip() and
                request.GET.get("genre", "") != "Any"):
            qs = qs.filter(
                genre__icontains=request.GET.get("genre", "").strip()
            )
        if (request.GET.get("year", "").strip() and
                request.GET.get("year", "") != "Any"):
            qs = qs.filter(
                release_date__gte=request.GET.get("year", "1991") + "-01-01",
                release_date__lte=request.GET.get("year", "2091") + "-12-31"
            )
        if (request.GET.get("min", "").strip() and
                float(request.GET.get("min", "")) > 0):
            qs = qs.filter(
                rating__gte=float(request.GET.get("min", "").strip())
            )
        if (request.GET.get("max", "").strip() and
                float(request.GET.get("max", "")) < 5):
            qs = qs.filter(
                rating__lte=float(request.GET.get("max", "").strip())
            )
        if (request.GET.get("board_min", "").strip() and
                int(request.GET.get("board_min", "")) >= 0 and
                request.GET.get("board_min", "") != ""):
            if (request.GET.get("board_type", "") == "playable"):
                qs = qs.filter(
                    playable_boards__gte=int(request.GET.get("board_min", "").strip())
                )
            else:
                qs = qs.filter(
                    total_boards__gte=int(request.GET.get("board_min", "").strip())
                )
        if (request.GET.get("board_max", "").strip() and
                int(request.GET.get("board_max", "")) <= 32767 and
                request.GET.get("board_min", "") != ""):
            if (request.GET.get("board_type", "") == "playable"):
                qs = qs.filter(
                    playable_boards__lte=int(request.GET.get("board_max", "").strip())
                )
            else:
                qs = qs.filter(
                    total_boards__lte=int(request.GET.get("board_max", "").strip())
                )
        if (request.GET.getlist("details")):
            qs = qs.filter(details__id__in=request.GET.getlist("details"))

        # Select distinct IDs
        qs = qs.distinct()

        # Show results
        sort = SORT_CODES[request.GET.get("sort", "title").strip()]
        if data["view"] == "list":
            data["files"] = qs.order_by(*sort)

            destination = "museum_site/browse_list.html"
        else:
            data["files"] = qs.order_by(*sort)[
                (data["page"] - 1) * PAGE_SIZE:data["page"] * PAGE_SIZE
            ]
            data["count"] = qs.count()
            data["pages"] = int(1.0 * math.ceil(data["count"] / PAGE_SIZE))
            data["page_range"] = range(1, data["pages"] + 1)
            data["prev"] = max(1, data["page"] - 1)
            data["next"] = min(data["pages"], data["page"] + 1)

            if data["view"] == "gallery":
                destination = "museum_site/browse_gallery.html"
            else:
                destination = "museum_site/browse.html"

    # Set page view cookie
    response = render(request, destination, data)
    response.set_cookie("view", data["view"], expires=datetime(3000, 12, 31))
    return response


def site_credits(request):
    """ Returns page for site credits """
    data = {"title": "Credits"}

    # Get all article authors
    data["authors"] = Article.objects.exclude(author="N/A").distinct().values_list("author", flat=True)
    data["list"] = []
    for author in data["authors"]:
        split = author.split("/")
        for name in split:
            if name not in data["list"]:
                data["list"].append(name)
    data["list"].sort(key=str.lower)
    data["split"] = math.ceil(len(data["list"]) / 4.0)
    return render(request, "museum_site/credits.html", data)


def upload(request):
    data = {"title": "Upload"}
    data["genres"] = GENRE_LIST

    if not UPLOADS_ENABLED:
        return redirect("/")

    print(request.POST.get("action"))
    print(request.FILES)
    if request.POST.get("action") == "upload" and request.FILES.get("file"):
        print("In func")
        upload = File()
        upload_resp = upload.from_request(request)

        if upload_resp.get("status") != "success":
            data["error"] = upload_resp["msg"]
            return render(request, "museum_site/upload.html", data)

        # Upload limit
        if request.FILES.get("file").size > UPLOAD_CAP:
            data["error"] = "Uploaded file size is too large. Contact staff for a manual upload."

            return render(request, "museum_site/upload.html", data)

        try:
            upload.full_clean(exclude=["publish_date"])
            upload.save(new_upload=True)

            # Flag it as an upload
            upload.details.add(Detail.objects.get(pk=18)) # TODO: Unhardcode #
            return redirect("/uploaded#" + upload.filename)
        except ValidationError as e:
            data["results"] = e
            print(data["results"])
    print("Done with func")
    return render(request, "museum_site/upload.html", data)


def uploaded_redir(request, filename):
    file = File.objects.get(filename=filename)
    return redirect(file.file_url())


def debug(request):
    data = {"title": "DEBUG PAGE"}

    #results = File.objects.filter(Q(author="Dr. Dos") | Q(review))
    print("Found", len(results), "by me")
    data["results"] = results

    return render(request, "museum_site/debug.html", data)


def debug_article(request):
    data = {"id": 0}
    with open("/var/projects/museum/private/" + request.GET.get("file")) as fh:
        article = Article.objects.get(pk=1)
        article.title = "TEST ARTICLE"
        article.category = "TEST"
        article.content = fh.read().replace("<!--PAGE-->", "<hr>")
        article.type = request.GET.get("format", "django")
    data["article"] = article
    data["veryspecial"] = True
    return render(request, "museum_site/article_view.html", data)
