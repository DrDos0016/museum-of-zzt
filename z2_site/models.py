# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.db import models
from django.template.defaultfilters import slugify

class Article(models.Model):
    title       = models.CharField(max_length=50)
    author      = models.CharField(max_length=50)
    category    = models.CharField(max_length=50)
    content     = models.TextField(default="")
    css         = models.TextField(default="", blank=True)
    type        = models.CharField(max_length=4) # text/html    
    date        = models.DateField(default="1970-01-01")
    published   = models.BooleanField(default=False)
    page        = models.IntegerField(default=1)
    
    def url(self):
        return "/article/"+str(self.id)+"/"+slugify(self.title)
    
class File(models.Model):
    letter      = models.CharField(max_length=1, db_index=True)    # #/A-Z to show up under when browsed
    filename    = models.CharField(max_length=50)   # Respite.zip
    title       = models.CharField(max_length=80)   # Frost 1: Power
    author      = models.CharField(max_length=80)   # Zenith Nadir/Hercules (/ sep)
    size        = models.IntegerField(default=0)    # Filesize in Kilobytes
    genre       = models.CharField(max_length=80, blank=True, default="")   # RPG/Action/Arcade (/ sep)
    release_date= models.DateField(default=None, null=True) # Release date
    release_source = models.CharField(max_length=20, null=True, default=None, blank=True) # ZZT file, News post, Text File, etc
    category    = models.CharField(max_length=10)   # ZZT, Super ZZT, ZIG, Soundtrack, Utility
    screenshot  = models.CharField(max_length=80, blank=True, null=True, default=None)   # Screenshot of title screen
    company     = models.CharField(max_length=80, default="", blank=True)   # Interactive Fantasies
    description = models.TextField(null=True, default=None) # Description for Utilites/Featured Games
    review_count= models.IntegerField(default=0)    # Number of reviews on this file
    rating      = models.FloatField(null=True, default=None, blank=True) # Rating if any, from reviews given
    details     = models.ManyToManyField("Detail")
    articles    = models.ManyToManyField("Article")    
    
    def __unicode__(self):
        return str(self.id) + " " + self.title
    
    def download_url(self):
        return "/zgames/" + self.letter + "/" + self.filename
        
    def play_url(self):
        return "/play/" + self.letter + "/" + self.filename
        
    def review_url(self):
        return "/review/" + self.letter + "/" + self.filename
        
    def file_url(self):
        if self.category != "Uploaded":
            return "/file/" + self.letter + "/" + self.filename
        else:
            return "/file/!/" + self.filename
        
    def wiki_url(self):
        return "http://zzt.org/zu/wiki/" + self.title
        
    def get_detail_ids(self):
        details = self.details.all()
        output = []
        for detail in details:
            output.append(int(detail.id))
        return output
        
    def author_list(self):
        return self.author.split("/")
        
    def genre_list(self):
        return self.genre.split("/")
    

class Detail(models.Model):
    detail      = models.CharField(max_length=20)
    
class Review(models.Model):
    file        = models.ForeignKey("File")         # Review file
    title       = models.CharField(max_length=50)   # Review title
    author      = models.CharField(max_length=50)   # Review author
    email       = models.EmailField()               # Contact info for author (hide this? Optional?)
    content     = models.TextField()                # Review content
    rating      = models.FloatField(default=5.0)    # Review Rating
    date        = models.DateField()                # Review Date
    ip          = models.GenericIPAddressField()    # Review IP
    
    def __unicode__(self):
        x = "Review for " + self.file.title + "[" + self.file.filename + "]\n"
        x+= self.title + "\n"
        x+= self.author + "\n"
        x+= self.email + "\n"
        x+= self.content[:50] + "..." + "\n"
        x+= str(self.rating) + "\n"  
        x+= str(self.date) + "\n"
        x+= self.ip + "\n"
        return x