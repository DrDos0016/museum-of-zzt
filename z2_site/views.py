# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.shortcuts import render
from .common import *

def advanced_search(request):
    """ Returns page containing multiple filters to use when searching """
    data = {"mode":"search", "genres":GENRE_LIST, "years":range(1991, YEAR+1)}

    return render(request, "z2_site/advanced_search.html", data)

def article(request, letter, filename):
    """ Returns page listing all articles associated with a provided file.
    If there is just one article, display it instead.
    """
    data = {}
    data["file"] = get_object_or_404(File, letter=letter, filename=filename)
    data["articles"] = data["file"].articles.all()
    data["letter"] = letter

    if len(data["articles"]) == 1:
        return article_view(request, data["articles"][0].id)
    else:
        return render(request, "z2_site/article.html", data)

def article_directory(request):
    """ Returns page listing all articles sorted either by date or name """
    data = {}
    data["sort"] = request.GET.get("sort", "category")
    if request.GET.get("sort") == "date":
        data["articles"] = Article.objects.defer("content", "css").filter(published=True, page=1).order_by("-date", "title")
        return render(request, "z2_site/article_directory.html", data)
    else:
        data["articles"] = Article.objects.defer("content", "css").filter(published=True, page=1).order_by("category", "title")
        return render(request, "z2_site/article_directory.html", data)

def article_view(request, id):
    """ Returns an article pulled from the database """
    id = int(id)
    data = {"id":id}
    data["article"] = get_object_or_404(Article, pk=id)
    data["title"] = data["article"].title
    file = data["article"].file_set.all()
    if file:
        data["file"] = file[0] # TODO: How to properly handle an article covering multiple files (ex Zem + Zem 2)
    return render(request, "z2_site/article_view.html", data)

def browse(request, letter="a", category="ZZT", page=1):
    """ Returns page containing a list of files filtered by letter, category, and page

    Keyword arguments:
    letter      -- The letter to filter by, may be a-z or 1 for numeric titled games. Default 'a'
    category    -- Category of files to filter by, may be ZZT, Super ZZT, ZIG, Soundtrack, Utility. Default 'ZZT'
    page        -- Page of results to slice to. Default '1'

    letter and page arguments are only used when the category is ZZT due to small sizes of other categories
    """
    data = {"mode":"browse", "category":category, "show_description": (category == "Utility")}

    print("Q count:", connection.queries)

    if category == "ZZT":
        if request.GET.get("view") == "list":
            data["letter"] = letter if letter != "1" else "#"
            data["files"] = File.objects.filter(category=category, letter=letter).order_by("title")
            destination = "z2_site/browse_list.html"
        else:
            data["page"] = int(request.GET.get("page", page))
            data["letter"] = letter if letter != "1" else "#"
            data["files"] = File.objects.filter(category=category, letter=letter).order_by("title")[(data["page"]-1)*PAGE_SIZE:data["page"]*PAGE_SIZE]
            data["count"] = File.objects.filter(category=category, letter=letter).count()
            data["pages"] = int(math.ceil(1.0 * data["count"] / PAGE_SIZE))
            data["page_range"] = range(1, data["pages"] + 1)
            data["prev"] = max(1,data["page"] - 1)
            data["next"] = min(data["pages"],data["page"] + 1)
            destination = "z2_site/browse.html"
    else:
        data["files"] = File.objects.filter(category=category).order_by("title")

        if request.GET.get("view") == "list":
            destination = "z2_site/browse_list.html"
        else:
            destination = "z2_site/browse.html"

    print("Q count:", connection.queries)
    return render(request, destination, data)

def directory(request, category):
    """ Returns a directory of all authors/companies/genres in the database """
    data = {}
    data["category"] = category
    
    """ This can possibly be cached in some way, it's not going to change
    often.
    """
    data_list = []
    if category == "company":
        companies = File.objects.values("company").exclude(company=None).exclude(company="").distinct().order_by("company")
        for c in companies:
            split = c["company"].split("/")
            for credited in split:
                if credited not in data_list:
                    data_list.append(credited)
    elif category == "author":
        authors = File.objects.values("author").distinct().order_by("author")
        for a in authors:
            split = a["author"].split("/")
            for credited in split:
                if credited not in data_list:
                    data_list.append(credited)
    elif category == "genre":
        genres = File.objects.values("genre").distinct().order_by("genre")
        for g in genres:
            split = g["genre"].split("/")
            for genre in split:
                if genre not in data_list:
                    data_list.append(genre)
    
    data_list = sorted(data_list, key=lambda k: k.lower())
    
    # Break the list of results into 4 columns
    data["list"] = data_list
    data["split"] = math.ceil(len(data["list"]) / 4.0)
    print("Length of list", len(data["list"]))
    print("Length / 4", len(data["list"]) / 4.0)
    return render(request, "z2_site/directory.html", data)
    

def featured_games(request, page=1):
    """ Returns a page listing all games marked as Featured """
    data = {}
    data["category"] = "ZZT"
    data["no_list"] = True
    data["page"] = int(request.GET.get("page", page))
    featured = Detail.objects.get(pk=7)
    data["featured"] = featured.file_set.all().order_by("title").prefetch_related("articles").defer("articles__content")[(data["page"]-1)*PAGE_SIZE:data["page"]*PAGE_SIZE]
    data["count"] = featured.file_set.all().count()
    data["pages"] = int(math.ceil(1.0 * data["count"] / PAGE_SIZE))
    data["page_range"] = range(1, data["pages"] + 1)
    data["prev"] = max(1,data["page"] - 1)
    data["next"] = min(data["pages"],data["page"] + 1)
    data["show_description"] = True
    data["show_featured"] = True

    return render(request, "z2_site/featured_games.html", data)

def file(request, letter, filename):
    """ Returns page exploring a file's zip contents """
    data = {}
    data["year"] = YEAR
    data["file"] = get_object_or_404(File, letter=letter, filename=filename)
    data["letter"] = letter
    zip = zipfile.ZipFile(os.path.join(SITE_ROOT, "zgames", letter, filename))
    data["files"] = zip.namelist()
    data["files"].sort()
    data["load_file"] = request.GET.get("file")
    data["load_board"] = request.GET.get("board")

    """ DEBUG, DO NOT USE ON PRODUCTION """
    data["save" ] = request.GET.get("screenshot")
    """ END DEBUG """

    #return render_to_response("file.html", data)
    return render(request, "z2_site/file.html", data)

def index(request):
    """ Returns front page """
    data = {}
    return render(request, "z2_site/index.html", data)

def play(request, letter, filename):
    """ Returns page to play file on archive.org """
    data = {}
    data["file"] = get_object_or_404(File, letter=letter, filename=filename)
    data["letter"] = letter

    return render(request, "z2_site/play.html", data)

def random(request):
    """ Returns a random file page """
    count = File.objects.count() # TODO: Filter this to only ZZT Worlds

    file = None
    while not file:
        id = randint(1,count)
        file = File.objects.filter(pk=id)
        if file:
            file = file[0]

    return redirect("file/"+file.letter+"/"+file.filename)

def review(request, letter, filename):
    """ Returns a page of reviews for a file """
    data = {}
    data["file"] = get_object_or_404(File, letter=letter, filename=filename)
    data["reviews"] = Review.objects.filter(file_id=data["file"].id)
    data["letter"] = letter
    return render(request, "z2_site/review.html", data)

def search(request):
    """ Searches database files. Returns the browse page filtered appropriately. """
    data = {"mode":"search"}

    # Strip page param from query string
    data["qs"] = request.GET.copy()
    if "page" in data["qs"]:
        data["qs"].pop("page")
    data["qs"] = data["qs"].urlencode()

    if request.GET.get("q"): # Basic Search
        q = request.GET["q"].strip()
        data["q"] = request.GET["q"]
        qs = File.objects.filter(
                Q(title__icontains=q) | Q(author__icontains=q) | Q(filename__icontains=q) | Q(company__icontains=q),
                category="ZZT"
            )
        if request.GET.get("view") == "list":
            data["files"] = qs.order_by("title")

            return render(request, "z2_site/browse_list.html", data)
        else:
            data["page"] = int(request.GET.get("page", 1))
            data["files"] = qs.order_by("title")[(data["page"]-1)*PAGE_SIZE:data["page"]*PAGE_SIZE]
            data["count"] = qs.count()
            data["pages"] = int(1.0 * math.ceil(data["count"] / PAGE_SIZE))
            data["page_range"] = range(1, data["pages"] + 1)
            data["prev"] = max(1,data["page"] - 1)
            data["next"] = min(data["pages"],data["page"] + 1)
            return render(request, "z2_site/browse.html", data)
    else: # Advanced Search
        # TODO: Handle <exact> in situations with multiple authors/companies
        qs = File.objects.all()
        if request.GET.get("title", "").strip():
            qs = qs.filter(title__icontains=request.GET.get("title", "").strip())
        if request.GET.get("author", "").strip():
            if request.GET.get("exact"):
                qs = qs.filter(author=request.GET.get("author", "").strip())
            else:
                qs = qs.filter(author__icontains=request.GET.get("author", "").strip())
        if request.GET.get("filename", "").strip():
            qs = qs.filter(filename__icontains=request.GET.get("filename", "").replace(".zip", "").strip())
        if request.GET.get("company", "").strip():
            qs = qs.filter(company__icontains=request.GET.get("company", "").strip())
        if request.GET.get("genre", "").strip() and request.GET.get("genre", "") != "Any":
            qs = qs.filter(genre__icontains=request.GET.get("genre", "").strip())
        if request.GET.get("year", "").strip() and request.GET.get("year", "") != "Any":
            qs = qs.filter(release_date__gte=request.GET.get("year","1991")+"-01-01", release_date__lte=request.GET.get("year", "2091")+"-12-31")
        if request.GET.get("min", "").strip() and float(request.GET.get("min", "")) > 0:
            qs = qs.filter(rating__gte=float(request.GET.get("min", "").strip()))
        if request.GET.get("max", "").strip() and float(request.GET.get("max", "")) < 5:
            qs = qs.filter(rating__lte=float(request.GET.get("max", "").strip()))
        if request.GET.get("category", "").strip() and request.GET.get("category", "") != "Any":
            qs = qs.filter(category=request.GET.get("category", "").strip())

        # Show results
        sort = request.GET.get("sort", "title").strip()
        if request.GET.get("view") == "list":
            data["files"] = qs.order_by(sort)

            return render(request, "z2_site/browse_list.html", data)
        else:
            data["page"] = int(request.GET.get("page", 1))
            data["files"] = qs.order_by(sort)[(data["page"]-1)*PAGE_SIZE:data["page"]*PAGE_SIZE]
            data["count"] = qs.count()
            data["pages"] = int(1.0 * math.ceil(data["count"] / PAGE_SIZE))
            data["page_range"] = range(1, data["pages"] + 1)
            data["prev"] = max(1,data["page"] - 1)
            data["next"] = min(data["pages"],data["page"] + 1)

            return render(request, "z2_site/browse.html", data)

def upload(request):
    data = {}
    data["genres"] = GENRE_LIST

    if request.POST.get("action") == "upload" and request.FILES.get("file"):

        # Form stuff
        title = request.POST.get("title", "").strip()

        # Get letter
        l_title = title.lower()
        if l_title[:4] == "the ":
            l_title = l_title[4:]
        elif l_title[:3] == " an":
            l_title = l_title[3:]
        elif l_title[:2] == "a ":
            l_title = l_title[2:]

        if l_title[0] in "abcdefghijklmnopqrstuvwxyz":
            letter = l_title[0]
        elif l_title[0] in "1234567890":
            letter = "1"
        else:
            for char in l_title:
                if char in "abcdefghijklmnopqrstuvwxyz":
                    letter = char
                    break

        # Get authors
        raw_authors = request.POST.get("author", "").strip().split("/")
        authors = ""
        for author in raw_authors:
            authors += author.strip()+"/"
        authors = authors[:-1]

        company = request.POST.get("company", "")

        # Get genres
        raw_genres = request.POST.getlist("genre", [])
        genres = ""
        for genre in raw_genres:
            if genre in GENRE_LIST:
                genres += genre.strip()+"/"
        genres = genres[:-1]

        # Get release date
        release_date = request.POST.get("release_date", "")
        try:
            datetime.strptime(release_date, "%Y-%m-%d")
        except:
            release_date = None

        if request.POST.get("desc", ""):
            description = "<p>" + request.POST.get("desc", "").replace("\n\n", "</p><p>").replace("\n", "<br>")+"</p"
        else:
            description = ""

        file = File(title=title, letter=letter, author=author,
            company=company, genre=genres, release_date=release_date, release_source="Uploader",
            description=description, category="Uploaded")

        # File stuff
        uploaded = request.FILES["file"]
        filename = uploaded.name
        size = int(uploaded.size / 1024)

        print(request.FILES)
        print(uploaded.name)
        print(uploaded.content_type)
        print(uploaded.size)


        # Upload limit
        if uploaded.size > UPLOAD_CAP:
            return HttpResponse("Uploaded file is too large!")

        zip = zipfile.ZipFile(uploaded) # TODO Proper path + os.path.join()

        file_list = zip.namelist()
        file_list.sort()
        print("ZIP CONTENTS")
        print(file_list)
        use_file = None
        for f in file_list:
            if f.lower()[-4:] == ".zzt":
                use_file = f
                break

        if not use_file:
            screenshot = None
        else:
            print("Ok working w/ this file")
            # Extract it
            zip.extract(use_file, ZZT2PNG_TEMP)
            screenshot_path = SITE_ROOT+"assets/images/screenshots/"+letter+"/"+os.path.splitext(filename)[0]
            #command = "python "+ZZT2PNG_PATH+" "+ZZT2PNG_TEMP+use_file + " 0 " + SITE_ROOT+"zgames/"+letter+"/"+os.path.splitext(filename)[0]
            command = "/usr/local/bin/python "+ZZT2PNG_PATH+" "+ZZT2PNG_TEMP+use_file + " 0 " + screenshot_path
            print("ZZT2PNG COMMAND:", command)
            os.system(command)

            if os.path.isfile(SITE_ROOT+"assets/images/screenshots/"+letter+"/"+os.path.splitext(filename)[0]+".png") and os.path.getsize(SITE_ROOT+"assets/images/screenshots/"+letter+"/"+os.path.splitext(filename)[0]+".png") > 0:
                screenshot = os.path.splitext(filename)[0]+".png"

        # -------------------------------------------

        try:
            file.filename = filename
            file.size = size
            file.screenshot = screenshot
            file.full_clean()
            file.save()
            return redirect("/uploaded#"+filename)
        except ValidationError as e:
            data["results"] = e

        print(title)
        print(author)
        print(company)
        print(genres)
        print(release_date)
        print(description)

    return render(request, "z2_site/upload.html", data)

def debug_save(request):
    letter = request.POST.get("letter")
    zip = request.POST.get("zip")
    img = request.POST.get("screenshot")[22:]

    fh = open("/var/projects/z2/assets/images/screenshots/"+letter+"/"+zip[:-4]+".png", "wb")
    fh.write(img.decode("base64"))
    fh.close()

    file = File.objects.get(letter=letter, filename=zip)
    file.screenshot = zip[:-4]+".png"
    file.save()

    return HttpResponse("<title>OK!</title>Saved "+zip)
