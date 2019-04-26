from django.conf.urls import url

from museum.settings import DEBUG
if DEBUG:
    from django.conf.urls.static import static

import museum_site.admin
import museum_site.ajax
import museum_site.errors
import museum_site.views
import museum_site.tools


from museum_site.models import (
    DETAIL_DOS,
    DETAIL_WIN16,
    DETAIL_WIN32,
    DETAIL_WIN64,
    DETAIL_LINUX,
    DETAIL_OSX,
    DETAIL_FEATURED,
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
    DETAIL_UPLOADED,
)

urlpatterns = [
    url(r"^$", museum_site.views.index, name="index"),
    url(r"^credits$", museum_site.views.site_credits),
    url(r"^data-integrity$", museum_site.views.generic, {"template": "data", "title":"Data Integrity"}, name="data_integrity"),

    # Accounts
    url(r"^register$", museum_site.views.register, name="register"),

    # Articles
    url(r"^article$", museum_site.views.article_directory,
        name="article_directory"
        ),
    url(r"^article/(?P<category>[a-z- ]+)$",
        museum_site.views.article_directory,
        name="article_directory"
        ),

    url(r"^article/(?P<id>[0-9]+)/page/(?P<page>[0-9]+)/(.*)$",
        museum_site.views.article_view,
        name="article_view_page"),
    url(r"^article/(?P<id>[0-9]+)/(.*)$",
        museum_site.views.article_view,
        {"page": 1},
        name="article_view",),

    # Special Article Pages (those with urls besides /article/#/title)
    url(r"^about-zzt$", museum_site.views.article_view, {"id": 1}),
    url(r"^ascii$", museum_site.views.article_view, {"id": 3}),
    url(r"^clones$", museum_site.views.article_view, {"id": 6}),
    url(r"^zzt-cheats$", museum_site.views.article_view, {"id": 22}, name="zzt_cheats"),
    url(r"^credits$", museum_site.views.article_view, {"id": 164}, name="credits"),
    url(r"^getting-started$", museum_site.views.article_view, {"id": 5}),
    url(r"^zzt$", museum_site.views.article_view, {"id": 2}, name="zzt_dl"),

    # Closer Looks
    url(r"^closer-looks$", museum_site.views.closer_look, name="closer_looks"),
    url(r"^livestreams$", museum_site.views.livestreams, name="livestreams"),

    # Directories
    url(r"^directory/(?P<category>[a-z].*)$", museum_site.views.directory,
        name="directory"
        ),

    # Featured Games
    url(r"^featured$", museum_site.views.featured_games, name="featured_games"),

    # Files
    url(r"^article/(?P<letter>[a-z1!])/(?P<filename>.*)$",
        museum_site.views.article,
        name="article"
        ),
    url(r"^browse/(?P<letter>[a-z1])$", museum_site.views.browse),
    url(r"^file/(?P<letter>[a-z1!])/(?P<filename>.*)$", museum_site.views.file,
        name="file"
        ),
    url(r"^file/uploaded/(?P<filename>.*)$", museum_site.views.uploaded_redir,
        name="redir_file"
        ),
    url(r"^play/(?P<letter>[a-z1!])/(?P<filename>.*)$", museum_site.views.play,
        name="play"
        ),
    url(r"^file/local$", museum_site.views.file,
        {"local": True, "letter":"!", "filename":""},
        name="local",
        ),

    # Files (alternate categories)
    url(r"^zzt-worlds$", museum_site.views.browse, {"details": [DETAIL_ZZT]},
        name="zzt_worlds"),
    url(r"^super-zzt$", museum_site.views.browse, {"details": [DETAIL_SZZT]},
        name="szzt_worlds"),
    url(r"^utilities$", museum_site.views.browse, {"details": [DETAIL_UTILITY], "show_description": True},
        name="utilities"),
    url(r"^zzm-audio$", museum_site.views.browse, {"details": [DETAIL_ZZM]},
        name="zzm_audio"),
    url(r"^zig-worlds$", museum_site.views.browse, {"details": [DETAIL_ZIG]},
        name="zig_worlds"),
    url(r"^contest-worlds$", museum_site.views.browse,
        {"details": [DETAIL_CONTEST]},
        name="contest_worlds"),
    url(r"^etc$", museum_site.views.browse, {"details": [DETAIL_ETC]},
        name="etc"),
    url(r"^modified-gfx$", museum_site.views.browse, {"details": [DETAIL_GFX]},
        name="modified_gfx"),
    url(r"^modified-exe$", museum_site.views.browse, {"details": [DETAIL_MOD]},
        name="modified_exe"),
    url(r"^osx$", museum_site.views.browse, {"details": [DETAIL_OSX]},
        name="osx"),
    url(r"^linux$", museum_site.views.browse, {"details": [DETAIL_LINUX]},
        name="linux"),
    url(r"^ms-dos$", museum_site.views.browse, {"details": [DETAIL_DOS]},
        name="ms_dos"),
    url(r"^win16$", museum_site.views.browse, {"details": [DETAIL_WIN16]},
        name="win16"),
    url(r"^win32$", museum_site.views.browse, {"details": [DETAIL_WIN32]},
        name="win32"),
    url(r"^win64$", museum_site.views.browse, {"details": [DETAIL_WIN64]},
        name="win64"),
    url(r"^lost-worlds$", museum_site.views.browse, {"details": [DETAIL_LOST]},
        name="lost_worlds"),
    url(r"^uploaded$", museum_site.views.browse, {"details": [DETAIL_UPLOADED]},
        name="uploaded_worlds"),

    url(r"^new$", museum_site.views.browse,
        name="new_files"),

    # Mass Downloads
    url(r"^mass-downloads$", museum_site.views.mass_downloads,
        name="mass_downloads"),

    # Patrons Only
    url(r"^patron-plans$", museum_site.views.patron_plans, name="patron_plans"),

    # Policies
    url(r"^policy/correction$", museum_site.views.generic, {"template": "correction_policy", "title":"Correction Policy"}, name="correction_policy"),
    url(r"^policy/removal$", museum_site.views.generic, {"template": "removal_policy", "title":"Removal Policy"}, name="removal_policy"),
    url(r"^policy/review$", museum_site.views.generic, {"template": "review_policy", "title":"Review Policy"}, name="review_policy"),
    url(r"^policy/upload$", museum_site.views.generic, {"template": "upload_policy", "title":"Upload Policy"}, name="upload_policy"),

    # Random ZZT World
    url(r"^random$", museum_site.views.random, name="random"),

    # Reviews
    url(r"^review/(?P<letter>[a-z1])/(?P<filename>.*)$", museum_site.views.review),

    # Search
    url(r"^advanced-search$", museum_site.views.advanced_search,
        name="advanced_search"
        ),
    url(r"^search$", museum_site.views.search, name="search"),

    # Uploads
    url(r"^upload$", museum_site.views.upload),

    # Zeta Live
    url(r"^zeta-live$", museum_site.views.zeta_live),

    ###########################################################################
    ###########################################################################

    # AJAX
    url(r"^ajax/get_zip_file$", museum_site.ajax.get_zip_file),

    # Redirects
    url(r"^twitter$", museum_site.views.redir, {"url": "https://twitter.com/worldsofzzt"}),
    url(r"^tumblr$", museum_site.views.redir, {"url": "http://worldsofzzt.tumblr.com"}),
    url(r"^discord$", museum_site.views.redir, {"url": "https://discordapp.com/invite/Nar4Upf"}),
    url(r"^patreon$", museum_site.views.redir, {"url": "https://patreon.com/worldsofzzt"}),
    url(r"^youtube$", museum_site.views.redir, {"url": "https://www.youtube.com/channel/UCr0f-r1bRexAZK8sWyk4NJA"}),
    url(r"^twitch$", museum_site.views.redir, {"url": "https://twitch.tv/worldsofzzt"}),
    url(r"^github$", museum_site.views.redir, {"url": "https://github.com/DrDos0016/z2"}),

    # Tools
    url(r"^tools/(?P<pk>[0-9]+)$", museum_site.tools.tool_list, name="tool_list"),
    url(r"^tools/mirror/(?P<pk>[0-9]+)$", museum_site.tools.mirror, name="mirror"),
    url(r"^tools/publish/(?P<pk>[0-9]+)$", museum_site.tools.publish, name="publish"),
    url(r"^tools/scan$", museum_site.tools.scan, name="scan"),
    url(r"^tools/set_screenshot/(?P<pk>[0-9]+)$", museum_site.tools.set_screenshot, name="set_screenshot"),

    # url(r"^staff/file_management$", museum_site.staff.file_management),
    # url(r"^staff/article_management$", museum_site.staff.article_management),

    # Debug
    url(r"^debug$", museum_site.views.debug),
    url(r"^debug/article$", museum_site.views.debug_article),
    url(r"^debug/z0x$", museum_site.views.debug_z0x),
    url(r"^ajax/debug_file$", museum_site.ajax.debug_file),

    url(r"^error/(?P<status>[0-9]+)$", museum_site.errors.raise_error)
]

if DEBUG:
    urlpatterns += static("/zgames", document_root="/var/projects/museum/zgames/")
