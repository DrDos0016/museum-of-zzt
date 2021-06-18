import os

from django.conf.urls import url

from museum.settings import BASE_DIR, DEBUG
if DEBUG:
    from django.conf.urls.static import static

import museum_site.admin
import museum_site.ajax
import museum_site.article_views
import museum_site.debug_views
import museum_site.file_views
# import museum_site.errors
import museum_site.feeds
import museum_site.help_views
import museum_site.review_views
import museum_site.search_views
import museum_site.tool_views
import museum_site.user_views
import museum_site.upload_views
import museum_site.views
import museum_site.zeta_views



from museum_site.constants import (
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
    url(r"^data-integrity$", museum_site.views.generic, {"template": "policy-data", "title":"Data Integrity"}, name="data_integrity"),

    # Articles
    url(r"^article$", museum_site.article_views.article_directory,
        name="article_directory"
        ),
    url(r"^article/search$", museum_site.search_views.article_search,
        name="article_search"
        ),
    url(r"^article/(?P<category>[a-z- ]+)$",
        museum_site.article_views.article_directory,
        name="article_directory"
        ),

    url(r"^article/(?P<article_id>[0-9]+)/page/(?P<page>[0-9]+)/(.*)$",
        museum_site.article_views.article_view,
        name="article_view_page"),
    url(r"^article/(?P<article_id>[0-9]+)/(.*)$",
        museum_site.article_views.article_view,
        {"page": 1},
        name="article_view",),

    # Special Article Pages (those with urls besides /article/#/title)
    url(r"^about-zzt$", museum_site.article_views.article_view, {"article_id": 534}, name="about_zzt"),
    url(r"^ascii$", museum_site.article_views.article_view, {"article_id": 3}, name="ascii"),
    url(r"^clones$", museum_site.article_views.article_view, {"article_id": 6}, name="clones"),
    url(r"^zzt-cheats$", museum_site.article_views.article_view, {"article_id": 22}, name="zzt_cheats"),
    url(r"^credits$", museum_site.article_views.article_view, {"article_id": 164}, name="credits"),
    url(r"^getting-started$", museum_site.article_views.article_view, {"article_id": 5}, name="zzt_dosbox"),
    url(r"^zzt$", museum_site.article_views.article_view, {"article_id": 2}, name="zzt_dl"),
    url(r"^zeta$", museum_site.article_views.article_view, {"article_id": 399}, name="zeta"),

    # Collections
    url(r"^collection/play$", museum_site.views.play_collection,
        name="play_collection"
        ),

    # Closer Looks
    url(r"^closer-looks$", museum_site.article_views.article_directory, {"category": "Closer Look"}, name="closer_looks"),
    url(r"^livestreams$", museum_site.article_views.article_directory, {"category": "Livestream"}, name="livestreams"),

    # Directories
    url(r"^directory/(?P<category>[a-z].*)$", museum_site.views.directory,
        name="directory"
        ),

    # Exhibit
    url(r"^exhibit/(?P<letter>[a-z1!])/(?P<filename>.*)$", museum_site.views.exhibit,
        name="exhibit"
        ),
    url(r"^exhibit/(?P<letter>[a-z1!])/(?P<filename>.*)/(?P<section>.*)$", museum_site.views.exhibit,
        name="exhibit-section"
        ),

    # Files
    url(r"^article/(?P<letter>[a-z1!])/(?P<filename>.*)$",
        museum_site.file_views.file_articles,
        name="article"
        ),
    url(r"^browse$", museum_site.file_views.file_directory, name="browse"),
    url(r"^browse/(?P<letter>[a-z1])$", museum_site.file_views.file_directory, name="browse_letter"),
    url(r"^file/(?P<letter>[a-z1!])/(?P<filename>.*)$", museum_site.file_views.file_viewer,
        name="file"
        ),
    url(r"^play/(?P<letter>[a-z1!])/(?P<filename>.*)$", museum_site.zeta_views.zeta_launcher,
        {"components": ["credits", "controls", "instructions", "players"]},
        name="play"
        ),
    url(r"^file/local$", museum_site.file_views.file_viewer,
        {"local": True, "letter":"!", "filename":""},
        name="local_file",
        ),

    # Files (alternate categories)
    url(r"^zzt-worlds$", museum_site.file_views.file_directory, {"details": [DETAIL_ZZT]},
        name="zzt_worlds"),
    url(r"^super-zzt$", museum_site.file_views.file_directory, {"details": [DETAIL_SZZT]},
        name="szzt_worlds"),
    url(r"^utilities$", museum_site.file_views.file_directory, {"details": [DETAIL_UTILITY], "show_description": True},
        name="utilities"),
    url(r"^zzm-audio$", museum_site.file_views.file_directory, {"details": [DETAIL_ZZM]},
        name="zzm_audio"),
    url(r"^zig-worlds$", museum_site.file_views.file_directory, {"details": [DETAIL_ZIG]},
        name="zig_worlds"),
    url(r"^etc$", museum_site.file_views.file_directory, {"details": [DETAIL_ETC]},
        name="etc"),
    url(r"^modified-gfx$", museum_site.file_views.file_directory, {"details": [DETAIL_GFX]},
        name="modified_gfx"),
    url(r"^modified-exe$", museum_site.file_views.file_directory, {"details": [DETAIL_MOD]},
        name="modified_exe"),
    url(r"^osx$", museum_site.file_views.file_directory, {"details": [DETAIL_OSX]},
        name="osx"),
    url(r"^linux$", museum_site.file_views.file_directory, {"details": [DETAIL_LINUX]},
        name="linux"),
    url(r"^ms-dos$", museum_site.file_views.file_directory, {"details": [DETAIL_DOS]},
        name="ms_dos"),
    url(r"^win16$", museum_site.file_views.file_directory, {"details": [DETAIL_WIN16]},
        name="win16"),
    url(r"^win32$", museum_site.file_views.file_directory, {"details": [DETAIL_WIN32]},
        name="win32"),
    url(r"^win64$", museum_site.file_views.file_directory, {"details": [DETAIL_WIN64]},
        name="win64"),
    url(r"^lost-worlds$", museum_site.file_views.file_directory, {"details": [DETAIL_LOST]},
        name="lost_worlds"),
    url(r"^uploaded/$", museum_site.file_views.file_directory, {"details": [DETAIL_UPLOADED]},
        name="uploaded_worlds"),
    url(r"^featured$", museum_site.file_views.file_directory, {"details": [DETAIL_FEATURED], "show_description": True, "show_featured": True},
        name="featured_games"),

    url(r"^new/$", museum_site.file_views.file_directory,
        name="new_files"),
    url(r"^new-releases/$", museum_site.file_views.file_directory,
        name="new_releases"),

    # Help
    url(r"^help/genres$", museum_site.help_views.genres,
        name="help_genre"),

    # Mass Downloads
    url(r"^mass-downloads$", museum_site.views.mass_downloads,
        name="mass_downloads"),

    # Patrons Only
    url(r"^patron-articles$", museum_site.article_views.patron_articles, name="patron_articles"),
    url(r"^patreon-pledge-drive$", museum_site.views.patreon_pledge_drive, name="patreon_pledge_drive"),

    # Policies
    url(r"^policy/correction$", museum_site.views.generic, {"template": "policy-correction", "title":"Correction Policy"}, name="correction_policy"),
    url(r"^policy/removal$", museum_site.views.generic, {"template": "policy-removal", "title":"Removal Policy"}, name="removal_policy"),
    url(r"^policy/review$", museum_site.views.generic, {"template": "policy-review", "title":"Review Policy"}, name="review_policy"),
    url(r"^policy/upload$", museum_site.views.generic, {"template": "policy-upload", "title":"Upload Policy"}, name="upload_policy"),

    # Random ZZT Worlds
    url(r"^random$", museum_site.views.random, name="random"),
    url(r"^roulette$", museum_site.file_views.roulette, {"details": [DETAIL_ZZT]}, name="roulette"),

    # Reviews
    url(r"^review$", museum_site.review_views.review_directory, name="review_directory"),
    url(r"^review/(?P<letter>[a-z1])/(?P<filename>.*)$", museum_site.file_views.review, name="reviews"),

    # Search
    url(r"^advanced-search$", museum_site.search_views.advanced_search,
        name="advanced_search"
        ),
    url(r"^deep-search$", museum_site.search_views.deep_search,
        name="deep_search"
        ),
    url(r"^search$", museum_site.search_views.search, name="search"),

    # User
    url("user/login/", museum_site.user_views.login_user, name="login_user"),
    url("user/logout/", museum_site.user_views.logout_user, name="logout_user"),
    url(r"^user/profile/(?P<user_id>[0-9]+)/", museum_site.user_views.user_profile, name="user_profile"),
    url("user/profile/", museum_site.user_views.user_profile, name="my_profile"),
    url("user/forgot-username/", museum_site.user_views.forgot_username, name="forgot_username"),
    url("user/forgot-username/complete/", museum_site.user_views.user_profile, name="forgot_username_complete"),
    url("user/forgot-password/", museum_site.user_views.forgot_password, name="forgot_password"),
    url("user/reset-password/complete/", museum_site.views.generic, {"template": "user-reset-password-complete", "title":"Reset Password Complete"}, name="reset_password_complete"),
    url("user/reset-password/(?P<token>.*)/", museum_site.user_views.reset_password, name="reset_password_with_token"),
    url("user/reset-password/", museum_site.user_views.reset_password, name="reset_password"),
    url("user/activate-account/(?P<token>.*)/", museum_site.user_views.activate_account, name="activate_account_with_token"),
    url("user/activate-account/", museum_site.user_views.activate_account, name="activate_account"),
    url("user/resend-activation/", museum_site.user_views.resend_account_activation, name="resend_activation"),
    url("user/change-char/", museum_site.user_views.change_char, name="change_char"),
    url("user/change-email/", museum_site.user_views.change_email, name="change_email"),
    url("user/change-password/", museum_site.user_views.change_password, name="change_password"),
    url("user/change-username/", museum_site.user_views.change_username, name="change_username"),
    url("user/change-patronage-visibility/", museum_site.user_views.change_patronage_visibility, name="change_patronage_visibility"),
    url("user/change-pronouns/", museum_site.user_views.change_pronouns, name="change_pronouns"),
    url("user/change-credit-preferences/", museum_site.user_views.change_credit_preferences, name="change_credit_preferences"),

    # World of ZZT
    url(r"^worlds-of-zzt$", museum_site.views.worlds_of_zzt_queue, name="worlds_of_zzt"),

    # Uploads
    url(r"^upload/$", museum_site.upload_views.upload, name="upload"),
    url(r"^upload/complete/$", museum_site.upload_views.upload_complete, name="upload_complete"),

    # Zeta Live
    url(r"^zeta-live$", museum_site.zeta_views.zeta_live),
    url(r"^zeta-launcher$", museum_site.zeta_views.zeta_launcher),

    ###########################################################################
    ###########################################################################

    # AJAX
    url(r"^ajax/deep-search/phase-(?P<phase>[0-9])$", museum_site.ajax.deep_search),
    url(r"^ajax/get_zip_file$", museum_site.ajax.get_zip_file),
    url(r"^ajax/wozzt_queue_add$", museum_site.ajax.wozzt_queue_add),
    url(r"^ajax/render-review-text$", museum_site.ajax.render_review_text),

    # RSS
    url("^rss/$", museum_site.views.generic, {"template": "rss-info", "title":"RSS Feeds"}, name="rss_feeds"),
    url("^rss/articles/$", museum_site.feeds.LatestArticlesFeed(), name="rss_articles"),
    url("^rss/files/$", museum_site.feeds.LatestFilesFeed(), name="rss_files"),
    url("^rss/reviews/$", museum_site.feeds.LatestReviewsFeed(), name="rss_reviews"),
    url("^rss/uploads/$", museum_site.feeds.LatestUploadsFeed(), name="rss_uploads"),

    # Redirects
    url(r"^twitter$", museum_site.views.redir, {"url": "https://twitter.com/worldsofzzt"}),
    url(r"^tumblr$", museum_site.views.redir, {"url": "http://worldsofzzt.tumblr.com"}),
    url(r"^discord$", museum_site.views.redir, {"url": "https://discordapp.com/invite/Nar4Upf"}, name="discord_invite"),
    url(r"^patreon$", museum_site.views.redir, {"url": "https://patreon.com/worldsofzzt"}, name="patreon"),
    url(r"^youtube$", museum_site.views.redir, {"url": "https://www.youtube.com/c/WorldsofZZT"}),
    url(r"^twitch$", museum_site.views.redir, {"url": "https://twitch.tv/worldsofzzt"}),
    url(r"^github$", museum_site.views.redir, {"url": "https://github.com/DrDos0016/z2"}),

    # Tools
    url(r"^tools/$", museum_site.tool_views.tool_index, name="tool_index"),
    url(r"^tools/(?P<pk>[0-9]+)$", museum_site.tool_views.tool_list, name="tool_list"),
    url(r"^tools/add-livestream/(?P<pk>[0-9]+)$", museum_site.tool_views.add_livestream, name="add_livestream"),
    url(r"^tools/audit/zeta-config$", museum_site.tool_views.audit_zeta_config, name="audit_zeta_config"),
    url(r"^tools/extract-font/(?P<pk>[0-9]+)$", museum_site.tool_views.extract_font, name="extract_font"),
    url(r"^tools/log-viewer$", museum_site.tool_views.log_viewer, name="log_viewer"),
    url(r"^tools/mirror/(?P<pk>[0-9]+)$", museum_site.tool_views.mirror, name="mirror"),
    url(r"^tools/publish/(?P<pk>[0-9]+)$", museum_site.tool_views.publish, name="publish"),
    url(r"^tools/reletter/(?P<pk>[0-9]+)$", museum_site.tool_views.reletter, name="reletter"),
    url(r"^tools/replace_zip/(?P<pk>[0-9]+)$", museum_site.tool_views.replace_zip, name="replace_zip"),
    url(r"^tools/scan$", museum_site.tool_views.scan, name="scan"),
    url(r"^tools/set_screenshot/(?P<pk>[0-9]+)$", museum_site.tool_views.set_screenshot, name="set_screenshot"),
    url(r"^tools/user-list$", museum_site.tool_views.user_list, name="user_list"),

    # Debug
    url(r"^debug$", museum_site.debug_views.debug),
    url(r"^debug/article$", museum_site.debug_views.debug_article),
    url(r"^debug/colors$", museum_site.debug_views.debug_colors),
    url(r"^debug/forms$", museum_site.views.generic, {"template": "debug-forms", "title":"Form Debug"}),
    url(r"^ajax/debug_file$", museum_site.ajax.debug_file),

    #url(r"^error/(?P<status>[0-9]+)$", museum_site.errors.raise_error)
]

if DEBUG:
    urlpatterns += static("/zgames", document_root=os.path.join(BASE_DIR, "zgames"))
