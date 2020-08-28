from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from .common import *
from .constants import *
from .models import *


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
    """ Returns page listing all articles associated with a provided file. """
    data = {}
    data["file"] = File.objects.get(letter=letter, filename=filename)
    data["title"] = data["file"].title + " - Articles"
    data["articles"] = data["file"].articles.all()
    data["letter"] = letter

    return render(request, "museum_site/article.html", data)


def article_directory(request, category="all", page_num=1):
    """ Returns page listing all articles sorted either by date or name """
    data = {"title": "Article Directory"}
    data["sort"] = request.GET.get("sort", "date")
    data["view"] = get_view_format(request)
    page_num = request.GET.get("page", page_num)

    # Query strings
    data["qs_sans_page"] = qs_sans(request.GET, "page")
    data["qs_sans_view"] = qs_sans(request.GET, "view")

    articles = Article.objects.defer("content", "css").filter(
        published=PUBLISHED_ARTICLE
    )

    if data["sort"] == "date":
        articles = articles.order_by("-date", "title")
    elif data["sort"] == "category":
        articles = articles.order_by("category", "title")
    else:
        articles = articles.order_by("title")

    if category != "all":
        articles = articles.filter(
            category=category.replace("-", " ").title()
        )

    # Limit articles
    page_size = PAGE_SIZE if data["view"] == "detailed" else LIST_PAGE_SIZE
    p = Paginator(articles, page_size)
    data["page"] = p.get_page(page_num)
    data["articles"] = data["page"].object_list

    # Determine destination template
    if data["view"] == "list":
        destination = "museum_site/article_directory_list.html"
    else:  # Detailed
        destination = "museum_site/article_directory.html"

    response = render(request, destination, data)
    # Set page view cookie
    response.set_cookie(
        "article_view",
        data["view"],
        expires=datetime(3000, 12, 31)
    )

    return response


def article_view(request, id, page=0):
    """ Returns an article pulled from the database """
    id = int(id)
    if id == 1:
        uri = request.build_absolute_uri()
        if uri.lower().endswith(".zip"):
            return article(request, "1", uri.split("/")[-1])

    slug = request.path.split("/")[-1]
    page = int(page)
    data = {"id": id}
    data["custom_layout"] = "article"

    if request.GET.get("secret") is None:
        data["article"] = get_object_or_404(
            Article, pk=id, published=PUBLISHED_ARTICLE
        )
    elif request.GET.get("secret") == PASSWORD2DOLLARS:
        data["access"] = "early"
        data["article"] = get_object_or_404(
            Article,
            Q(published=PUBLISHED_ARTICLE) | Q(published=UPCOMING_ARTICLE),
            pk=id
        )
        data["private_disclaimer"] = True

    elif request.GET.get("secret") == PASSWORD5DOLLARS:
        data["access"] = "really_early"
        data["article"] = get_object_or_404(
            Article,
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

    zgames = data["article"].file_set.all()
    if zgames:
        # TODO: Handle an article w/ multiple files (ex Zem + Zem 2)
        data["file"] = zgames[0]

    # Split article to current page
    data["article"].content = data["article"].content.split(
        "<!--Page-->"
    )[data["page"]-1]
    return render(request, "museum_site/article_view.html", data)


def browse(
    request,
    letter=None,
    details=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UTILITY],
    page=1, show_description=False
):
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
        data["og_image"] = "images/new-preview.png"
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
        # Calculate upload queue size
        request.session["FILES_IN_QUEUE"] = File.objects.filter(details__id__in=[DETAIL_UPLOADED]).count()

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
        data["files"] = File.objects.filter(details__id__in=details).distinct()
        if letter:
            data["files"] = data["files"].filter(letter=letter)
        data["files"] = data["files"].order_by(*sort)
    else:  # Others list over multiple pages
        data["page"] = int(request.GET.get("page", page))
        data["letter"] = letter if letter != "1" else "#"
        data["files"] = File.objects.filter(details__id__in=details).distinct()
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
    # data["collection_params"] = populate_collection_params(data)
    # TODO: THIS IS COMMENTED OUT TO HIDE IT ON PRODUCTION

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


def deep_search(request):
    """ Returns page containing multiple filters to use when searching """
    data = {
        "title": "Deep Search",
        "mode": "search",
        "genres": GENRE_LIST,
        "years": [str(x) for x in range(1991, YEAR + 1)]
    }

    data["details_list"] = request.GET.getlist("details", ADV_SEARCH_DEFAULTS)
    return render(request, "museum_site/deep_search.html", data)


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
    # data_list = sorted(data_list, key=lambda s: s.lower())
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


def exhibit(request, letter, filename, section=None, local=False):
    """ Returns page exploring a file's zip contents """
    data = {}
    data["custom_layout"] = "fv-grid"
    data["year"] = YEAR
    data["details"] = []  # Required to show all download links
    data["file"] = File.objects.get(letter=letter, filename=filename)
    data["local"] = local
    if not local:
        data["title"] = data["file"].title
        data["letter"] = letter

        # Check for recommended custom charset
        if data["file"].id in list(CUSTOM_CHARSET_MAP.keys()):
            data["custom_charset"] = CUSTOM_CHARSET_MAP[data["file"].id]

        if data["file"].is_uploaded():
            letter = "uploaded"
            data["uploaded"] = True

        data["files"] = []

        if ".zip" in filename.lower():
            zip_file = zipfile.ZipFile(os.path.join(SITE_ROOT, "zgames", letter, filename))
            files = zip_file.namelist()
            files.sort(key=str.lower)
            data["zip_info"] = zip_file.infolist()

            # Filter out directories (but not their contents)
            for f in files:
                if f and f[-1] != os.sep:
                    data["files"].append(f)
            data["load_file"] = urllib.parse.unquote(request.GET.get("file", ""))
            data["load_board"] = request.GET.get("board", "")
    else:  # Local files
        data["file"] = "Local File Viewer"
        data["letter"] = letter

    data["charsets"] = CHARSET_LIST
    data["custom_charsets"] = CUSTOM_CHARSET_LIST

    return render(request, "museum_site/exhibit.html", data)


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

    # data["collection_params"] = populate_collection_params(data)
    # TODO: THIS IS COMMENTED OUT TO HIDE IT ON PRODUCTION

    return render(request, "museum_site/featured_games.html", data)


def file(request, letter, filename, local=False):
    """ Returns page exploring a file's zip contents """
    data = {}
    data["custom_layout"] = "fv-grid"
    data["year"] = YEAR
    data["details"] = []  # Required to show all download links
    data["local"] = local
    if not local:
        data["file"] = File.objects.get(letter=letter, filename=filename)
        data["title"] = data["file"].title
        data["letter"] = letter

        # Check for recommended custom charset
        for charset in CUSTOM_CHARSETS:
            if data["file"].id == charset["id"]:
                data["custom_charset"] = charset["filename"]
                break

        if data["file"].is_uploaded():
            letter = "uploaded"
            data["uploaded"] = True

        data["files"] = []

        if ".zip" in filename.lower():
            zip_file = zipfile.ZipFile(os.path.join(SITE_ROOT, "zgames", letter, filename))
            files = zip_file.namelist()
            files.sort(key=str.lower)
            data["zip_info"] = sorted(zip_file.infolist(), key=lambda k: k.filename.lower())

            # Filter out directories (but not their contents)
            for f in files:
                if f and f[-1] != os.sep:
                    data["files"].append(f)
            data["load_file"] = urllib.parse.unquote(request.GET.get("file", ""))
            data["load_board"] = request.GET.get("board", "")
    else:  # Local files
        data["file"] = "Local File Viewer"
        data["letter"] = letter

    data["charsets"] = []
    data["custom_charsets"] = []

    if not data["local"]:
        if data["file"].is_zzt():
            for charset in CHARSETS:
                if charset["engine"] == "ZZT":
                    data["charsets"].append(charset)
            for charset in CUSTOM_CHARSETS:
                if charset["engine"] == "ZZT":
                    data["custom_charsets"].append(charset)
        elif data["file"].is_super_zzt():
            for charset in CHARSETS:
                if charset["engine"] == "SZZT":
                    data["charsets"].append(charset)
            for charset in CUSTOM_CHARSETS:
                if charset["engine"] == "SZZT":
                    data["custom_charsets"].append(charset)
        elif data["file"].is_uploaded():
            data["charsets"] = CHARSETS
            data["custom_charsets"] = CUSTOM_CHARSETS
    # TODO LOCAL FILES CAN'T GET CHARSETS WITH THIS
    else:
        data["charsets"] = CHARSETS
        data["custom_charsets"] = CUSTOM_CHARSETS

    return render(request, "museum_site/file.html", data)


def generic(request, title="", template=""):
    data = {"title": title}
    return render(request, "museum_site/" + template + ".html")


def index(request):
    """ Returns front page """
    data = {}

    # Obtain latest content
    data["articles"] = Article.objects.filter(published=PUBLISHED_ARTICLE).order_by("-date")[:FP_ARTICLES_SHOWN]
    data["files"] = File.objects.all().exclude(details__id__in=[DETAIL_UPLOADED]).order_by("-publish_date", "-id")[:FP_FILES_SHOWN]
    data["reviews"] = Review.objects.all().order_by("-date")[:FP_REVIEWS_SHOWN]

    # Calculate upload queue size
    request.session["FILES_IN_QUEUE"] = File.objects.filter(details__id__in=[DETAIL_UPLOADED]).count()

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


def mass_downloads(request):
    """ Returns a page for downloading files by release year """
    data = {"title": "Mass Downloads"}
    # Read the json
    return render(request, "museum_site/mass_downloads.html", data)


def patron_articles(request):
    data = {}
    data["early"] = Article.objects.filter(published=UPCOMING_ARTICLE)
    data["really_early"] = Article.objects.filter(published=UNPUBLISHED_ARTICLE)
    data["og_image"] = "images/early-access-preview.png"

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
    data["file"] = File.objects.get(letter=letter, filename=filename)
    data["title"] = data["file"].title + " - Play Online"
    data["letter"] = letter

    # Find supported play methods
    all_play_methods = list(PLAY_METHODS.keys())
    compatible_players = []

    if "zeta" in all_play_methods:
        if data["file"].supports_zeta_player():
            compatible_players.append("zeta")
        elif data["file"].is_uploaded():
            # For unpublished worlds, assume yes but add a disclaimer
            compatible_players.append("zeta")
            data["unpublished"] = True

    if "archive" in all_play_methods:
        if data["file"].archive_name:
            compatible_players.append("archive")

    # Is there a manually selected preferred player?
    if request.GET.get("player") and request.GET.get("player") in all_play_methods:
        preferred_player = request.GET.get("player")
    else:  # If not, use Zeta as the default player
        preferred_player = "zeta"

    # Does the preferred player support this file?
    if preferred_player in compatible_players:
        player = preferred_player
    else:  # If not, force this hierarchy
        if "zeta" in compatible_players:
            player = "zeta"
        elif "archive" in compatible_players:
            player = "archive"
        else:
            player = "none"

    # Finalize the player
    data["player"] = player

    # Populate options for any alternative players
    data["players"] = {}
    for option in compatible_players:
        data["players"][option] = PLAY_METHODS[option]

    # Are we playing in pop-out mode?
    data["play_base"] = "museum_site/world.html"
    if request.GET.get("popout"):
        data["play_base"] = "museum_site/play-popout.html"

    # Override for "Live" Zeta edits
    if request.GET.get("live"):
        data["zeta_url"] = "/zeta-live?pk={}&world={}&start={}".format(
            data["file"].id,
            request.GET.get("world"),
            request.GET.get("start", 0)
        )
    elif request.GET.get("discord"):
        data["zeta_url"] = "/zeta-live?discord=1&world={}".format(
            request.GET.get("world")
        )

    # If you're using Zeta, select the proper executable
    if player == "zeta":
        if data["file"].is_super_zzt():
            data["engine"] = "szzt.zip"
        else:
            data["engine"] = "zzt.zip"
        data["zeta_database"] = str(data["file"].id)

    data["zeta_player_scale"] = int(request.COOKIES.get("zeta_player_scale", 1))

    response = render(request, "museum_site/play_{}.html".format(player), data)
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
            if data["file"] is None:
                data["file"] = f
            else:
                data["extra_files"] += '"{}",\n'.format(f.download_url())

    response = render(request, "museum_site/play_collection.html", data)
    return response


def random(request):
    """ Returns a random ZZT file page """
    max_pk = File.objects.all().order_by("-id")[0].id

    zgame = None
    while not zgame:
        id = randint(1, max_pk)
        zgames = File.objects.filter(pk=id, details__id=DETAIL_ZZT)
        if zgames:
            zgame = zgames[0]

    return redirect(zgame.file_url())


def redir(request, url):
    return redirect(url, permanent=True)


def register(request):
    data = {}
    return render(request, "museum_site/register.html", data)


def review(request, letter, filename):
    """ Returns a page of reviews for a file. Handles POSTing new reviews """
    data = {}
    data["file"] = File.objects.get(letter=letter, filename=filename)
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

        if request.GET["q"] == "+DEBUG":
            request.session["DEBUG"] = 1
        if request.GET["q"] == "-DEBUG":
            request.session["DEBUG"] = 0

        data["q"] = request.GET["q"]
        qs = File.objects.filter(
            Q(title__icontains=q) |
            Q(aliases__alias__icontains=q) |
            Q(author__icontains=q) |
            Q(filename__icontains=q) |
            Q(company__icontains=q)
        ).exclude(details__id__in=[DETAIL_UPLOADED]).distinct()

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

    # Convert POST genres to a list to easily recheck boxes on failed upload
    data["requested_genres"] = request.POST.getlist("genre")

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
            upload.details.add(Detail.objects.get(pk=DETAIL_UPLOADED))

            # Calculate upload queue size
            request.session["FILES_IN_QUEUE"] = File.objects.filter(details__id__in=[DETAIL_UPLOADED]).count()

            return redirect("/uploaded#" + upload.filename)
        except ValidationError as e:
            data["results"] = e
            print(data["results"])
    return render(request, "museum_site/upload.html", data)


def uploaded_redir(request, filename):
    zgame = File.objects.get(filename=filename)
    return redirect(zgame.file_url())


def zeta_live(request):
    if request.GET.get("discord"):
        with open("/var/projects/museum/museum_site/static/data/discord-zzt/" + request.GET.get("filename"), "rb") as fh:
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

    # temp_bytes.write(orig_file)

    # Extract the file
    # Adjust the file

    # Return it to Zeta
    temp_zip = BytesIO()

    # Create new zip
    with zipfile.ZipFile(temp_zip, "w") as mem_zip:
        # Using the basename of the filepath within the zip allows playing
        # something in a folder. It's hacky, but works.
        mem_zip.writestr(os.path.basename(fname), modded_file)

    response = HttpResponse(content_type="application/octet-stream")
    response["Content-Disposition"] = "attachment; filename=TEST.ZIP"
    response.write(temp_zip.getvalue())
    return response

@staff_member_required
def worlds_of_zzt_queue(request):
    data = {"title": "Worlds of ZZT Queue"}
    category = request.GET.get("category", "wozzt")

    if request.user.is_staff:
        if request.POST.get("action"):
            if request.POST["action"] == "roll":
                count = request.POST.get("count")
                category = request.POST.get("category")
                title = True if category == "tuesday" else False

                for x in range(0, int(count)):
                    WoZZT_Queue().roll(category=category, title_screen=title)

            elif request.POST["action"] == "set-priority":
                pk = int(request.POST.get("id"))
                entry = WoZZT_Queue.objects.get(pk=pk)
                entry.priority = int(request.POST.get("priority"))
                entry.save()

            elif request.POST["action"] == "delete":
                pk = int(request.POST.get("id"))
                entry = WoZZT_Queue.objects.get(pk=pk)
                entry.delete_image()
                entry.delete()

    data["queue"] = WoZZT_Queue.objects.filter(category=category).order_by("-priority", "id")
    data["queue_size"] = len(data["queue"])
    return render(request, "museum_site/wozzt-queue.html", data)


def zeta_launcher(request, letter=None, filename=None, components=["controls", "instructions", "credits", "advanced", "players"]):
    data = {"title": "Zeta Launcher"}
    # Template rendering mode
    # full - Extends "world.html", has a file header
    # popout - Extends "play-popout.html", removes all site components
    data["mode"] = request.GET.get("mode", "full")
    data["base"] = "museum_site/world.html"

    # Determine visible components
    data["components"] = {
        "controls": True if "controls" in components else False,
        "instructions": True if "instructions" in components else False,
        "credits": True if "credits" in components else False,
        "advanced": True if "advanced" in components else False,
        "players": True if "players" in components else False,
    }

    # Show advanced settings if requested in URL
    if request.GET.get("advanced"):
        data["components"]["advanced"] = True

    # Hide everything in popout mode and force Zeta
    if data["mode"] == "popout":
        data["base"] = "museum_site/play-popout.html"
        data["components"] = {
        "controls": False,
        "instructions": False,
        "credits": False,
        "advanced": False,
        "players": False,
        }
        player = "zeta"

    if data["components"]["advanced"]:
        #data["charsets"] = CUSTOM_CHARSET_LIST
        data["all_files"] = File.objects.filter(
            details__id__in=[DETAIL_ZZT, DETAIL_SZZT, DETAIL_UPLOADED]
        ).order_by("sort_title", "id").only("id", "title")

    data["charset_override"] = request.GET.get("charset_override", "")
    data["executable"] = request.GET.get("executable", "AUTO")
    data["engine"] = data["executable"]
    data["ZETA_EXECUTABLES"] = ZETA_EXECUTABLES

    # Get files requested
    if letter and filename:
        data["file"] = File.objects.get(letter=letter, filename=filename)
    else:
        data["file"] = None  # This will be the "prime" file

    data["file_ids"] = list(map(int, request.GET.getlist("file_id")))

    if (data["file"] and data["file"].id not in data["file_ids"]):
        data["file_ids"] = [data["file"].id] + data["file_ids"]

    data["file_count"] = len(data["file_ids"])
    data["included_files"] = []
    for f in File.objects.filter(pk__in=data["file_ids"]):
        data["included_files"].append(f.download_url())
        if data["file"] is None:
            data["file"] = f

    # Set the page title
    if data["file"]:
        data["title"] = data["file"].title + " - Play Online"

    if len(data["included_files"]) == 1:  # Use the file ID for the SaveDB
        data["zeta_database"] = f.id

    if data["components"]["players"]:
        # Find supported play methods
        all_play_methods = list(PLAY_METHODS.keys())
        compatible_players = []

        if "zeta" in all_play_methods:
            if data["file"].supports_zeta_player():
                compatible_players.append("zeta")
            elif data["file"].is_uploaded():
                # For unpublished worlds, assume yes but add a disclaimer
                compatible_players.append("zeta")
                data["unpublished"] = True

        if "archive" in all_play_methods:
            if data["file"].archive_name:
                compatible_players.append("archive")

        # Is there a manually selected preferred player?
        if request.GET.get("player") and request.GET.get("player") in all_play_methods:
            preferred_player = request.GET.get("player")
        else:  # If not, use Zeta as the default player
            preferred_player = "zeta"

        # Does the preferred player support this file?
        if preferred_player in compatible_players:
            player = preferred_player
        else:  # If not, force this hierarchy
            if "zeta" in compatible_players:
                player = "zeta"
            elif "archive" in compatible_players:
                player = "archive"
            else:
                player = "none"

        # Finalize the player
        data["player"] = player

        # Populate options for any alternative players
        data["players"] = {}
        for option in compatible_players:
            data["players"][option] = PLAY_METHODS[option]

    # Get info for all Zeta configs if needed
    if data["components"]["advanced"]:
        data["config_list"] = Zeta_Config.objects.only("id", "name")

    # Get Zeta Config for file
    data["zeta_config"] = data["file"].zeta_config
    if request.GET.get("zeta_config"):  # User override
        data["zeta_config"] = Zeta_Config.objects.get(pk=int(request.GET["zeta_config"]))

    # Override config with user requested options
    if data["zeta_config"]:
        data["zeta_config"].user_configure(request.GET)
    else:
        data["zeta_config"] = Zeta_Config.objects.get(pk=1)  # TODO make this a constant

    # Extra work for custom fonts
    if data["zeta_config"].name == "Custom Font - Generic":
        generic_font = ""
        zip_file = zipfile.ZipFile(os.path.join(data["file"].phys_path()))
        files = zip_file.namelist()
        for f in files:
            if f.lower().endswith(".com"):
                generic_font = f
        data["zeta_config"].commands = data["zeta_config"].commands.replace("{font_file}", generic_font)

    # Override for "Live" Zeta edits
    if request.GET.get("live"):
        data["zeta_live"] = True
        data["zeta_url"] = "/zeta-live?pk={}&world={}&start={}".format(
            data["file"].id,
            request.GET.get("world"),
            request.GET.get("start", 0)
        )
    elif request.GET.get("discord"):
        data["zeta_url"] = "/zeta-live?discord=1&world={}".format(
            request.GET.get("world")
        )

    # Set default scale
    data["zeta_player_scale"] = int(request.COOKIES.get("zeta_player_scale", 1))
    return render(request, "museum_site/play_{}.html".format(player), data)
