from datetime import datetime

from django.contrib.syndication.views import Feed
from django.db.models import Q
from django.urls import reverse
from django.template.defaultfilters import slugify

from museum_site.models import Article, File, Review


class Base_Feed(Feed):
    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.url()


class Latest_Articles_Feed(Base_Feed):
    title = "Museum of ZZT - Latest Articles RSS"
    link = "/article/"
    description = "Museum of ZZT article feed"

    def items(self):
        return Article.objects.published().order_by("-id")[:25]

    def item_pubdate(self, item):
        return datetime.combine(item.publish_date, datetime.min.time())

    def item_author_name(self, item):
        return item.author


class Upcoming_Articles_Feed(Latest_Articles_Feed):
    title = "Museum of ZZT - Latest/Upcoming Articles RSS"

    def items(self):
        return Article.objects.published_or_upcoming().order_by("-id")[:25]


class Unpublished_Articles_Feed(Latest_Articles_Feed):
    title = "Museum of ZZT - Latest/Upcoming/Unpublished Articles RSS"

    def items(self):
        return Article.objects.published_or_upcoming_or_unpublished().order_by("-id")[:25]


class Latest_Files_Feed(Base_Feed):
    title = "Museum of ZZT - Latest Published Files RSS"
    link = "/file/browse/"
    description = "Museum of ZZT published file feed"

    def items(self):
        return File.objects.published().order_by("-publish_date", "-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        output = "{} by {}".format(item.title, ", ".join(item.related_list("authors")))
        if item.release_date:
            output += " (" + str(item.release_date)[:4] + ")\n"
        else:
            output += "\n"
        if item.get_all_company_names():
            output += "Published by: " + str(item.get_all_company_names()) + "\n"
        return output

    def item_link(self, item):
        return item.url()

    def item_pubdate(self, item):
        return item.publish_date

    def item_author_name(self, item):
        return ", ".join(item.related_list("authors"))


class Latest_Reviews_Feed(Base_Feed):
    title = "Museum of ZZT - Latest Reviews RSS"
    link = "/review/"
    description = "Museum of ZZT review feed"

    def items(self):
        return Review.objects.latest_approved_reviews().order_by("-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        output = 'Review by {} covering "{}".'.format(item.get_author(), item.zfile.title)
        if item.rating >= 0:
            output += " ({}/5.0)".format(item.rating)
        return output

    def item_link(self, item):
        return item.url()

    def item_pubdate(self, item):
        return item.date

    def item_author_name(self, item):
        return item.get_author()


class Latest_Uploads_Feed(Base_Feed):
    title = "Museum of ZZT - Latest Uploaded Files RSS"
    link = "/file/browse/detail/uploaded/"
    description = "Museum of ZZT file upload feed"

    def items(self):
        return File.objects.unpublished().order_by("-id")[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        output = "{} by {}".format(item.title, ", ".join(item.related_list("authors")))
        if item.release_date:
            output += " (" + str(item.release_date)[:4] + ")\n"
        else:
            output += "\n"
        if item.get_all_company_names():
            output += "Published by: " + str(item.get_all_company_names()) + "\n"
        return output

    def item_link(self, item):
        return item.url()

    def item_pubdate(self, item):
        return item.upload.date

    def item_author_name(self, item):
        return ", ".join(item.related_list("authors"))
