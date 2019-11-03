from django.shortcuts import render
from .common import *
from .constants import *

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
    data = {"title": "Article Directory"}
    data["sort"] = request.GET.get("sort", "date")
    if data["sort"] == "date":
        data["articles"] = Article.objects.defer(
            "content", "css"
        ).filter(published=PUBLISHED_ARTICLE).order_by("-date", "title")
    else:
        data["articles"] = Article.objects.defer(
            "content", "css"
        ).filter(published=PUBLISHED_ARTICLE).order_by("category", "title")

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
    data["custom_layout"] = "article"

    if request.GET.get("secret") is None:
        data["article"] = get_object_or_404(Article, pk=id, published=PUBLISHED_ARTICLE)
    elif request.GET.get("secret") == PASSWORD2DOLLARS:
        data["access"] = "early"
        data["article"] = get_object_or_404(Article,
            Q(published=PUBLISHED_ARTICLE) |
            Q(published=UPCOMING_ARTICLE),
            pk=id
        )
        data["private_disclaimer"] = True

    elif request.GET.get("secret") == PASSWORD5DOLLARS:
        data["access"] = "really_early"
        data["article"] = get_object_or_404(Article,
            Q(published=PUBLISHED_ARTICLE) |
            Q(published=UPCOMING_ARTICLE) |
            Q(published=UNPUBLISHED_ARTICLE),
            pk=id,
        )
        data["private_disclaimer"] = True
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
        data["category"] = "ZZT"
    elif len(details) == 1:
        data["title"] = "Browse - " + CATEGORY_LIST[details[0]][1]
        data["category"] = CATEGORY_LIST[details[0]][1]
    else:
        data["title"] = "Browse"

    # Determine the viewing method
    data["view"] = get_view_format(request)

    sort = SORT_CODES[request.GET.get("sort", "title").strip()]

    # Handle special paths
    if request.path == "/new":
        data["mode"] = "new"
        data["title"] = "New Additions"
        data["category"] = "New Additions"
        sort = SORT_CODES["published"]
    elif request.path == "/roulette":
        sort = SORT_CODES["roulette"]
        data["mode"] = "roulette"
        data["title"] = "Roulette"
        data["rng_seed"] = str(int(request.GET.get("rng_seed", time())))
        data["category"] = "Roulette Seed " + data["rng_seed"]
    elif request.path == "/uploaded":
        data["mode"] = "uploaded"
        data["category"] = "Upload Queue"

    # Query strings
    data["qs_sans_page"] = qs_sans(request.GET, "page")
    data["qs_sans_view"] = qs_sans(request.GET, "view")

    # Append RNG seed if there is one
    if data.get("rng_seed") and "rng_seed" not in data["qs_sans_page"]:
        data["qs_sans_page"] += "&rng_seed=" + data["rng_seed"]
        data["qs_sans_view"] += "&rng_seed=" + data["rng_seed"]

    if request.path == "/roulette":
        ids = list(File.objects.filter(details__id__in=details).values_list("id", flat=True))
        seed(data["rng_seed"])
        shuffle(ids)
        data["files"] = File.objects.filter(id__in=ids[:PAGE_SIZE]).order_by("?")
    elif data["view"] == "list":  # List gets a full listing on one page
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

    # Determine destination template
    if data["view"] == "list":
        destination = "museum_site/browse_list.html"
    elif data["view"] == "gallery":
        destination = "museum_site/browse_gallery.html"
    else:  # Detailed
        destination = "museum_site/browse.html"

    # Determine params needed to play this collection of files
    #data["collection_params"] = populate_collection_params(data) TODO: THIS IS COMMENTED OUT TO HIDE IT ON PRODUCTION

    response = render(request, destination, data)

    # Set page view cookie
    response.set_cookie("view", data["view"], expires=datetime(3000, 12, 31))

    return response


def closer_look(request):
    """ Returns a listing of all Closer Look articles """
    data = {"title": "Closer Looks"}
    data["articles"] = Article.objects.filter(
        category="Closer Look", published=PUBLISHED_ARTICLE,
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
    data["count"] = Article.objects.filter(category="Closer Look", published=PUBLISHED_ARTICLE).count()
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
        data_list = GENRE_LIST

    # Break the list of results into 4 columns
    data_list = sorted(data_list, key=lambda s: re.sub(r'(\W|_)', "é", s.lower()))
    #data_list = sorted(data_list, key=lambda s: s.lower())
    first_letters = []

    for entry in data_list:
        if entry[0] in "1234567890":
            first_letters.append("#")
        elif entry[0].upper() not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            first_letters.append("*")
        else:
            first_letters.append(entry[0].upper())

    data["list"] = list(zip(data_list, first_letters))
    data["split"] = math.ceil(len(data_list) / 4.0)
    return render(request, "museum_site/directory.html", data)


def featured_games(request, page=1):
    """ Returns a page listing all games marked as Featured """
    data = {"title": "Featured Games"}
    data["mode"] = "featured"
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

    #data["collection_params"] = populate_collection_params(data) TODO: THIS IS COMMENTED OUT TO HIDE IT ON PRODUCTION

    return render(request, "museum_site/featured_games.html", data)


def file(request, letter, filename, local=False):
    """ Returns page exploring a file's zip contents """
    data = {}
    data["custom_layout"] = "fv-grid"
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
        data["load_file"] = urllib.parse.unquote(request.GET.get("file", ""))
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
    data["articles"] = Article.objects.filter(published=PUBLISHED_ARTICLE).order_by("-date")[:10]
    data["files"] = File.objects.all().exclude(details__id__in=[18]).order_by("-publish_date", "-id")[:12]  # TODO: Unhardcode
    data["reviews"] = Review.objects.all().order_by("-date")[:10]

    return render(request, "museum_site/index.html", data)

def livestreams(request):
    """ Returns a listing of all Livestream articles """
    data = {"title": "Livestreams"}
    data["articles"] = Article.objects.filter(
        category="Livestream", published=PUBLISHED_ARTICLE
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
    data["count"] = Article.objects.filter(category="Livestream", published=PUBLISHED_ARTICLE).count()
    data["pages"] = int(math.ceil(1.0 * data["count"] / PAGE_SIZE))
    data["page_range"] = range(1, data["pages"] + 1)
    data["prev"] = max(1, data["page"] - 1)
    data["next"] = min(data["pages"], data["page"] + 1)
    data["qs_sans_page"] = qs_sans(request.GET, "page")
    return render(request, "museum_site/livestreams.html", data)


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


def patron_articles(request):
    data = {}
    data["early"] = Article.objects.filter(published=UPCOMING_ARTICLE)
    data["really_early"] = Article.objects.filter(published=UNPUBLISHED_ARTICLE)

    if request.POST.get("secret") == PASSWORD2DOLLARS:
        data["access"] = "early"
    elif request.POST.get("secret") == PASSWORD5DOLLARS:
        data["access"] = "really_early"
    elif request.POST.get("secret") is not None:
        data["wrong_password"] = True


    return render(request, "museum_site/patreon_articles.html", data)


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

    player = request.GET.get("player")
    if player is None or player not in player_names:
        # If no player was provided, check for a cookie preference
        preferred_player = request.COOKIES.get("preferred_player", "")
        if preferred_player not in player_names:
            player = "zeta"  # Default player
        else:
            player = preferred_player

    # Check player compatibility
    cookie_preferred = player  # In case the user's choice isn't available
    data["fallback"] = False

    if player == "zeta":
        if not data["file"].supports_zeta_player:
            player = "archive"
            data["fallback"] = True
    elif player == "archive":
        if not data["file"].archive_name:
            player = "zeta"
            data["fallback"] = True

    # The player the page will use
    data["player"] = player
    data["players"] = PLAY_METHODS

    if data["file"].id in CUSTOM_CHARSET_MAP:
        data["custom_charset"] = CUSTOM_CHARSET_MAP[data["file"].id]
    else:
        data["custom_charset"] = None

    if player == "zeta":
        if data["file"].is_super_zzt():
            data["engine"] = "szzt.zip"
        else:
            data["engine"] = "zzt.zip"
        data["zeta_database"] = str(data["file"].id)

    data["play_base"] = "museum_site/world.html"
    if request.GET.get("popout"):
        data["play_base"] = "museum_site/play-popout.html"

    # Override for "Live" Zeta edits
    if request.GET.get("live"):
        data["zeta_url"] = "/zeta-live?pk={}&world={}&start={}".format(data["file"].id, request.GET.get("world"), request.GET.get("start", 0))
    elif request.GET.get("discord"):
        data["zeta_url"] = "/zeta-live?discord=1&world={}".format(request.GET.get("world"))

    response = render(request, "museum_site/play.html", data)
    response.set_cookie("preferred_player", cookie_preferred, expires=datetime(3000, 12, 31))
    return response


def play_collection(request):
    """ Returns page to play file in the browser """
    data = {}
    data["title"] = " - Play Collection"
    data["player"] = "zeta"  # Must be Zeta
    data["custom_charset"] = None  # Modified graphics aren't really viable here
    data["engine"] = "zzt.zip"  # TODO: Special case for SZZT
    data["play_base"] = "museum_site/world.html"

    if request.GET.get("letter"):
        data["letter"] = request.GET.get("letter")

    if request.GET.get("popout"):
        data["play_base"] = "museum_site/play-popout.html"

    # Get the files in the collection
    if request.GET.get("mode") == "featured":
        files = File.objects.filter(details__id__in=[DETAIL_FEATURED])
    elif request.GET.get("mode") == "new":
        files = File.objects.all().order_by(*SORT_CODES["published"])
    elif request.GET.get("mode") == "browse":
        files = File.objects.filter(letter=data["letter"])

    # TODO: WEIRDLY BROKEN TITLES
    files = files.exclude(pk=431)  # 4 by Jojoisjo
    files = files.exclude(pk=85)  # Banana Quest


    # Slice by page

    data["page"] = int(request.GET.get("page", 1))
    data["files"] = files[
        (data["page"] - 1) * PAGE_SIZE:data["page"] * PAGE_SIZE
    ]

    data["file"] = None
    data["extra_files"] = ""
    for f in data["files"][1:]:
        if f.file_exists():
            print("ADDING", f)
            print(f.phys_path())
            if data["file"] is None:
                data["file"] = f
            else:
                data["extra_files"] += '"{}",\n'.format(f.download_url())
        else:
            print("SKIPPING", f)

    print(data["extra_files"])

    response = render(request, "museum_site/play_collection.html", data)
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
        data["file"].calculate_reviews()
        data["file"].save()

    data["reviews"] = Review.objects.filter(file_id=data["file"].id)
    return render(request, "museum_site/review.html", data)


def search(request):
    """ Searches database files. Returns the browse page filtered
        appropriately.
    """
    data = {"mode": "search", "title": "Search"}
    data["category"] = "Search Results"
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

        # Auto redirect for Italicized-Links in Closer Looks
        if request.GET.get("auto"):
            qs.order_by("id")
            params = qs_sans(request.GET, "q")
            return redirect(qs[0].file_url() + "?" + params)

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
        # Clean up empty params
        if request.GET.get("advanced"):
            new_qs = "?"
            for k in request.GET.keys():
                if k in ["advanced", "details"]:
                    continue
                if k == "board_type" and not (request.GET.get("board_min") or request.GET.get("board_max")):
                    continue
                if k == "min" and request.GET[k] == "0.0":
                    continue
                if k == "max" and request.GET[k] == "5.0":
                    continue
                if request.GET[k] not in ["", "Any"]:
                    new_qs += k + "=" + request.GET[k] + "&"

            details = request.GET.getlist("details")
            for d in details:
                new_qs += "details=" + d + "&"
            new_qs = new_qs[:-1]
            return redirect("/search"+new_qs)

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
                request.GET.get("year", "") != "Any" and
                request.GET.get("year", "") != "Unk"):
            qs = qs.filter(
                release_date__gte=request.GET.get("year", "1991") + "-01-01",
                release_date__lte=request.GET.get("year", "2091") + "-12-31"
            )
        elif (request.GET.get("year", "").strip() == "Unk"):
            qs = qs.filter(release_date=None)
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
                request.GET.get("board_max", "") != ""):
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

    if request.POST.get("action") == "upload" and request.FILES.get("file"):
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
    return render(request, "museum_site/upload.html", data)


def uploaded_redir(request, filename):
    file = File.objects.get(filename=filename)
    return redirect(file.file_url())

def zeta_live(request):
    if request.GET.get("discord"):
        with open("/var/projects/museum/museum_site/static/data/discord-zzt/"+ request.GET.get("filename"), "rb") as fh:
            response = HttpResponse(content_type="application/octet-stream")
            response["Content-Disposition"] = "attachment; filename=DISCORD.ZIP"
            response.write(fh.read())
        return response

    pk = int(request.GET["pk"])
    fname = request.GET["world"]
    start = int(request.GET["start"]).to_bytes(1, byteorder="little")

    f = File.objects.get(pk=int(pk))

    temp_bytes = BytesIO()

    # Open original zip and extract the file
    with zipfile.ZipFile(f.phys_path()) as orig_zip:
        orig_file = orig_zip.read(fname)


    # Adjust starting board
    modded_file = orig_file[:17] + start + orig_file[18:]

    #temp_bytes.write(orig_file)

    # Extract the file
    # Adjust the file

    # Return it to Zeta
    temp_zip = BytesIO()

    # Create new zip
    with zipfile.ZipFile(temp_zip, "w") as mem_zip:
        mem_zip.writestr(fname, modded_file)

    response = HttpResponse(content_type="application/octet-stream")
    response["Content-Disposition"] = "attachment; filename=TEST.ZIP"
    response.write(temp_zip.getvalue())
    return response
