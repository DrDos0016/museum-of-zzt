# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from common import *

def article_directory(request):
    data = {}
    data["sort"] = request.GET.get("sort", "category")
    if request.GET.get("sort") == "date":
        data["articles"] = Article.objects.defer("content", "css").filter(published=True).order_by("date", "title")
        return render_to_response("article_directory.html", data)
    else:
        data["articles"] = Article.objects.defer("content", "css").filter(published=True).order_by("category", "title")
        return render_to_response("article_directory.html", data)
    
def article_view(request, id):
    id = int(id)
    data = {"id":id}
    data["article"] = get_object_or_404(Article, pk=id)
    data["title"] = data["article"].title
    return render_to_response("article_view.html", data)

def browse(request, letter="*", page=1):
    data = {}
    
    if request.GET.get("view") == "list":
        data["letter"] = letter if letter != "1" else "#"
        data["files"] = File.objects.filter(letter=letter).order_by("title")
        return render_to_response("browse_list.html", data)
    else:
        data["page"] = int(request.GET.get("page", page))
        data["letter"] = letter if letter != "1" else "#"
        data["files"] = File.objects.filter(letter=letter).order_by("title")[(data["page"]-1)*10:data["page"]*10]
        data["count"] = File.objects.filter(letter=letter).count()
        data["pages"] = int(math.ceil(data["count"] / 10.0))
        data["page_range"] = range(1, data["pages"] + 1)
        data["prev"] = max(1,data["page"] - 1)
        data["next"] = min(data["pages"],data["page"] + 1)
        return render_to_response("browse.html", data)

def featured_games(request):
    data = {}
    featured = Detail.objects.get(pk=7)
    data["featured"] = featured.file_set.all()
    
    return render_to_response("featured_games.html", data, context_instance=RequestContext(request))

def file(request, letter, filename):
    data = {}
    data["file"] = get_object_or_404(File, letter=letter, filename=filename)
    data["letter"] = letter
    zip = zipfile.ZipFile("/var/projects/z2/zgames/"+letter+"/"+filename) # TODO Proper path + os.path.join()
    data["files"] = zip.namelist()
    data["files"].sort()
    data["load_file"] = request.GET.get("file")
    data["load_board"] = request.GET.get("board")
    
    """ DEBUG, DO NOT USE ON PRODUCTION """
    data["save" ] = request.GET.get("screenshot")
    """ END DEBUG """
    
    #return render_to_response("file.html", data)
    return render_to_response("file.html", data, context_instance=RequestContext(request))

def index(request):
    data = {}
    return render_to_response("index.html", data)
    
def random(request):
    count = File.objects.count() # TODO: Filter this to only ZZT Worlds
    
    
    file = None
    while not file:
        id = randint(1,count)
        file = File.objects.filter(pk=id)
        if file:
            file = file[0]
    
    return redirect("file/"+file.letter+"/"+file.filename)
    
def review(request, letter, filename):
    data = {}
    data["file"] = get_object_or_404(File, letter=letter, filename=filename)
    data["reviews"] = Review.objects.filter(file_id=data["file"].id)
    data["letter"] = letter
    return render_to_response("review.html", data)
    
def upload(request):
    return render_to_response("upload.html", data)
    
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