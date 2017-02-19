# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.db import models
from django.contrib import admin
from django.template.defaultfilters import slugify


CATEGORY_LIST = (
    ("ZZT", "ZZT World"),
    ("ZZM", "ZZM Soundtrack"),
    ("ZIG", "ZIG World"),
    ("Utility", "External Utility"),
    ("SZZT", "Super ZZT World"),
    ("Etc", "Etc."),
)

DETAIL_DOS = 1
DETAIL_WIN16 = 2
DETAIL_WIN32 = 3
DETAIL_WIN64 = 4
DETAIL_LINUX = 5
DETAIL_OSX = 6
DETAIL_FEATURED = 7
DETAIL_CONTEST = 8
DETAIL_ZZM = 9
DETAIL_GFX = 10
DETAIL_MOD = 11
DETAIL_ETC = 12
DETAIL_SZZT = 13
DETAIL_UTILITY = 14
DETAIL_ZZT = 15
DETAIL_ZIG = 16
DETAIL_LOST = 17
DETAIL_UPLOADED = 18
DETAIL_REMOVED = 19


class Article(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    content = models.TextField(default="")
    css = models.TextField(default="", blank=True)
    type = models.CharField(max_length=4)  # text/html
    date = models.DateField(default="1970-01-01")
    published = models.BooleanField(default=False)
    page = models.IntegerField(default=1)
    parent = models.ForeignKey("Article", null=True, blank=True, default=None)
    content_warning = models.BooleanField(default=False)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title + " by " + self.author

    def url(self):
        return "/article/" + str(self.id) + "/" + slugify(self.title)

    def get_page_count(self):
        if self.parent_id == 0:
            page_count = 1 + Article.objects.filter(parent_id=self.id).count()
        else:
            page_count = 1 + Article.objects.filter(
                parent_id=self.parent_id
            ).count()
        return page_count


class File(models.Model):
    """ File object repesenting an upload to the site

    Fields:
    letter          -- Name of the (Zip) file (ex: Respite.zip)
    title           -- Name of the World (ex: Frost 1: Power)
    author          -- / sep. ABC list of authors (ex: Hercules/Nadir)
    size            -- Filesize in Kilobytes (ex: 42)
    genre           -- / sep. ABC list of genres (ex: Action/RPG)
    release_date    -- Best guess release date (ex: 2001-04-16)
    release_source  -- Source of release date (ex: ZZT file, News post, Text)
    category        -- What kind of file this is (ex: ZZT, Super ZZT, Utility)
    screenshot      -- Filename of screenshot to display (ex: 3dtalk.png)
    company         -- / sep. ABC list of companies published (ex: ERI/IF)
    description     -- Description of file for utilities or featured games
    review_count    -- Number of reviews on this file
    rating          -- Average rating if any, from file's reviews
    details         -- Link to Detail objects
    articles        -- Link to Article objects
    article_count   -- Number of articles associated with this file
    """

    letter = models.CharField(max_length=1, db_index=True)
    filename = models.CharField(max_length=50)
    title = models.CharField(max_length=80)
    author = models.CharField(max_length=80)
    size = models.IntegerField(default=0)
    genre = models.CharField(max_length=80, blank=True, default="")
    release_date = models.DateField(default=None, null=True, blank=True)
    release_source = models.CharField(
        max_length=20, null=True, default=None, blank=True
    )
    category = models.CharField(max_length=10, choices=CATEGORY_LIST)
    screenshot = models.CharField(
        max_length=80, blank=True, null=True, default=None
    )
    company = models.CharField(
        max_length=80, default="", blank=True, null=True
    )
    description = models.TextField(null=True, blank=True, default="")
    review_count = models.IntegerField(default=0)
    rating = models.FloatField(null=True, default=None, blank=True)
    details = models.ManyToManyField("Detail", default=None, blank=True)
    articles = models.ManyToManyField("Article", default=None, blank=True)
    article_count = models.IntegerField(default=0)
    checksum = models.CharField(max_length=32, null=True,
                                blank=True, default="")
    superceded = models.ForeignKey("File", db_column="superceded_id",
                                   null=True, blank=True, default=None)


    class Meta:
        ordering = ["title"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.title

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

    def article_url(self):
        return "/article/" + self.letter + "/" + self.filename

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
    detail = models.CharField(max_length=20)

    class Meta:
        ordering = ["detail"]

    def __str__(self):
        return "[" + str(self.id) + "] " + self.detail


class Review(models.Model):
    """ Review object repesenting an review to a file

    Fields:
    file            -- Link to File object
    title           -- Title of the review
    author          -- Author of the review
    email           -- Author's email (hide this? Optional?)
    content         -- Body of review
    rating          -- Rating given to file from 0.0 - 5.0
    """
    file = models.ForeignKey("File")
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    content = models.TextField()
    rating = models.FloatField(default=5.0)
    date = models.DateField()
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        x = ("[" + str(self.id) + "] Review for " + self.file.title + " [" +
             self.file.filename + "] by " + self.author
             )
        return x
