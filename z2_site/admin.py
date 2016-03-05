# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from common import *

def article_management(request):
    data = {}
    data["today"] = datetime.now()
    #if not request.user.is_staff:
    #    return redirect("/")
        
    if request.POST.get("action") == "save":
        if request.POST.get("article_id") == "NEW":
            article = Article()
        else:
            article = Article.objects.get(pk=request.POST.get("article_id"))
            
        # Set fields
        article.title       = request.POST.get("title")
        article.author      = request.POST.get("author")
        article.type        = request.POST.get("type")
        article.category    =request.POST.get("category")
        article.content     = request.POST.get("content")
        article.css         = request.POST.get("css")
        article.date        = request.POST.get("date")
        article.published   = request.POST.get("published", False)
        article.page        = request.POST.get("page", 1)
        article.file_id     = request.POST.get("file_id") if request.POST.get("file_id") else None
        
        try:
            article.full_clean(exclude=["file"])
            article.save()
            data["results"] = "Article successfully saved."
        except ValidationError as e:
            data["results"] = e
        data["article"] = article
    else:
        if request.GET.get("article_id") and request.GET.get("article_id") != "NEW":
            data["article"] = Article.objects.get(pk=request.GET.get("article_id"))
            
    data["articles"] = Article.objects.all().order_by("title")
    return render_to_response("admin/article_management.html", data, context_instance=RequestContext(request))
    

def file_management(request):
    data = {}
    data["today"] = datetime.now()
    #if not request.user.is_staff:
    #    return redirect("/")
        
    if request.POST.get("action") == "save":
        file = File.objects.get(pk=request.POST.get("file_id"))
            
        # Set fields
        
        # Handle Details
        print "="*40
        print "DETAILS"
        old_detail_list = request.POST.get("original_detail")[:-1].split(",")
        if old_detail_list[0] == "":
            old_detail_list = []
        detail_list = request.POST.getlist("detail")
        print "Old detail list:", old_detail_list
        print "New detail list:", detail_list
        
        for detail in old_detail_list:
            if detail not in detail_list:
                print "REMOVE DETAIL", detail
                file.details.remove(int(detail))
                
        for detail in detail_list:
            if detail not in old_detail_list:
                print "ADD DETAIL", detail
                file.details.add(int(detail))
        
        try:
            #article.full_clean(exclude=["file"])
            #article.save()
            data["results"] = "File successfully saved."
        except ValidationError as e:
            data["results"] = e
        data["file"] = file
    else:
        if request.GET.get("letter") and request.GET.get("file_name"):
            data["file"] = File.objects.get(filename=request.GET["file_name"]+".zip", letter=request.GET["letter"])
            print "GOT A FILE"
            
            
    # Possible details
    data["details"] = Detail.objects.all().order_by("detail")
    return render_to_response("admin/file_management.html", data, context_instance=RequestContext(request))