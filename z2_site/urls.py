# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.conf.urls import url

import z2_site.admin
import z2_site.ajax
import z2_site.views

urlpatterns = [
    url(r"^$", z2_site.views.index, name="index"),
    url(r"^upload$", z2_site.views.upload),

    # Articles
    url(r"^article$", z2_site.views.article_directory,
        name="article_directory"
        ),
    url(r"^article/(?P<category>[a-z-]+)$", z2_site.views.article_directory,
        name="article_directory"
        ),
    url(r"^article/(?P<id>[0-9]+)/(.*)$", z2_site.views.article_view),

    # Special Article Pages (those with urls besides /article/#/title)
    url(r"^about-zzt$", z2_site.views.article_view, {"id": 1}),
    url(r"^ascii$", z2_site.views.article_view, {"id": 3}),
    url(r"^clones$", z2_site.views.article_view, {"id": 6}),
    url(r"^getting-started$", z2_site.views.article_view, {"id": 5}),
    url(r"^mass$", z2_site.views.article_view, {"id": 7}),
    url(r"^zzt$", z2_site.views.article_view, {"id": 2}),

    # Directories
    url(r"^directory/(?P<category>[a-z].*)$", z2_site.views.directory,
        name="directory"
        ),

    # Featured Games
    url(r"^featured$", z2_site.views.featured_games, name="featured_games"),

    # Files
    url(r"^article/(?P<letter>[a-z1!])/(?P<filename>.*)$",
        z2_site.views.article,
        name="article"
        ),
    url(r"^browse/(?P<letter>[a-z1])$", z2_site.views.browse),
    url(r"^file/(?P<letter>[a-z1!])/(?P<filename>.*)$", z2_site.views.file,
        name="file"
        ),
    url(r"^play/(?P<letter>[a-z1!])/(?P<filename>.*)$", z2_site.views.play,
        name="play"
        ),
    url(r"^superzzt$", z2_site.views.browse, {"category": "Super ZZT"}),
    url(r"^zig$", z2_site.views.browse, {"category": "ZIG"}),
    url(r"^soundtracks$", z2_site.views.browse, {"category": "Soundtrack"}),
    url(r"^uploaded$", z2_site.views.browse, {"category": "Uploaded"}),
    url(r"^utilities$", z2_site.views.browse, {"category": "Utility"}),

    # Random ZZT World
    url(r"^random$", z2_site.views.random, name="random"),

    # Reviews
    url(r"^review/(?P<letter>[a-z1])/(?P<filename>.*)$", z2_site.views.review),

    # Search
    url(r"^advanced-search$", z2_site.views.advanced_search,
        name="advanced_search"
        ),
    url(r"^search$", z2_site.views.search, name="search"),

    # Uploads
    url(r"^upload$", z2_site.views.upload),

    ###########################################################################
    ###########################################################################

    # AJAX
    url(r"^ajax/get_zip_file$", z2_site.ajax.get_zip_file),

    # Staff
    # url(r"^staff/file_management$", z2_site.staff.file_management),
    # url(r"^staff/article_management$", z2_site.staff.article_management),

    # Debug
    url(r"^debug/save$", z2_site.views.debug_save),
    url(r"^ajax/debug_file$", z2_site.ajax.debug_file),
]
