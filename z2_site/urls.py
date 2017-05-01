# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from django.conf.urls import url

import z2_site.admin
import z2_site.ajax
import z2_site.views

from z2_site.models import (
    DETAIL_DOS,
    DETAIL_WIN16,
    DETAIL_WIN32,
    DETAIL_WIN64,
    DETAIL_LINUX,
    DETAIL_OSX,
    # DETAIL_FEATURED,
    DETAIL_CONTEST,
    DETAIL_ZZM,
    DETAIL_GFX,
    DETAIL_MOD,
    DETAIL_ETC,
    DETAIL_SZZT,
    DETAIL_UTILITY,
    DETAIL_ZZT,
    DETAIL_ZIG,
    DETAIL_LOST,
    # DETAIL_UPLOADED,
)

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

    url(r"^article/(?P<id>[0-9]+)/page/(?P<page>[0-9]+)/(.*)$",
        z2_site.views.article_view,
        name="article_view_page"),
    url(r"^article/(?P<id>[0-9]+)/(.*)$",
        z2_site.views.article_view,
        {"page": 1},
        name="article_view",),

    # Special Article Pages (those with urls besides /article/#/title)
    url(r"^about-zzt$", z2_site.views.article_view, {"id": 1}),
    url(r"^ascii$", z2_site.views.article_view, {"id": 3}),
    url(r"^clones$", z2_site.views.article_view, {"id": 6}),
    url(r"^credits$", z2_site.views.article_view, {"id": 164}, name="credits"),
    url(r"^getting-started$", z2_site.views.article_view, {"id": 5}),
    url(r"^zzt$", z2_site.views.article_view, {"id": 2}, name="zzt_dl"),

    # Closer Looks
    url(r"^closer-looks$", z2_site.views.closer_look, name="closer_looks"),

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
    url(r"^file/local$", z2_site.views.local,
        name="local"
        ),

    # Files (alternate categories)
    url(r"^zzt-worlds$", z2_site.views.browse, {"details": [DETAIL_ZZT]},
        name="zzt_worlds"),
    url(r"^super-zzt$", z2_site.views.browse, {"details": [DETAIL_SZZT]},
        name="szzt_worlds"),
    url(r"^utilities$", z2_site.views.browse, {"details": [DETAIL_UTILITY]},
        name="utilities"),
    url(r"^zzm-audio$", z2_site.views.browse, {"details": [DETAIL_ZZM]},
        name="zzm_audio"),
    url(r"^zig-worlds$", z2_site.views.browse, {"details": [DETAIL_ZIG]},
        name="zig_worlds"),
    url(r"^contest-worlds$", z2_site.views.browse,
        {"details": [DETAIL_CONTEST]},
        name="contest_worlds"),
    url(r"^etc$", z2_site.views.browse, {"details": [DETAIL_ETC]},
        name="etc"),
    url(r"^modified-gfx$", z2_site.views.browse, {"details": [DETAIL_GFX]},
        name="modified_gfx"),
    url(r"^modified-exe$", z2_site.views.browse, {"details": [DETAIL_MOD]},
        name="modified_exe"),
    url(r"^osx$", z2_site.views.browse, {"details": [DETAIL_OSX]},
        name="osx"),
    url(r"^linux$", z2_site.views.browse, {"details": [DETAIL_LINUX]},
        name="linux"),
    url(r"^ms-dos$", z2_site.views.browse, {"details": [DETAIL_DOS]},
        name="ms_dos"),
    url(r"^win16$", z2_site.views.browse, {"details": [DETAIL_WIN16]},
        name="win16"),
    url(r"^win32$", z2_site.views.browse, {"details": [DETAIL_WIN32]},
        name="win32"),
    url(r"^win64$", z2_site.views.browse, {"details": [DETAIL_WIN64]},
        name="win64"),
    url(r"^lost-worlds$", z2_site.views.browse, {"details": [DETAIL_LOST]},
        name="lost_worlds"),

    # Mass Downloads
    url(r"^mass-downloads$", z2_site.views.mass_downloads,
        name="mass_downloads"),

    # Policies
    url(r"^policy/correction$", z2_site.views.article_view, {"id": 2}, name="correction_policy"),
    url(r"^policy/removal$", z2_site.views.article_view, {"id": 165}, name="removal_policy"),
    url(r"^policy/review$", z2_site.views.article_view, {"id": 165}, name="review_policy"),
    url(r"^policy/submission$", z2_site.views.article_view, {"id": 2}, name="submission_policy"),

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
    url(r"^debug$", z2_site.views.debug),
    url(r"^debug/save$", z2_site.views.debug_save),
    url(r"^debug/article$", z2_site.views.debug_article),
    url(r"^ajax/debug_file$", z2_site.ajax.debug_file),
]
