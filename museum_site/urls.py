import os

from django.views.generic.base import RedirectView
from django.urls import include, path
from django.conf.urls import url

from museum.settings import BASE_DIR, DEBUG
if DEBUG:
    from django.conf.urls.static import static

import museum_site.admin  # noqa: E402
import museum_site.ajax  # noqa: E402
import museum_site.article_views  # noqa: E402
import museum_site.debug_views  # noqa: E402
import museum_site.file_views  # noqa: E402
# import museum_site.errors  # noqa: E402
import museum_site.feeds  # noqa: E402
import museum_site.help_views  # noqa: E402
import museum_site.review_views  # noqa: E402
import museum_site.search_views  # noqa: E402
import museum_site.tool_views  # noqa: E402
import museum_site.user_views  # noqa: E402
import museum_site.upload_views  # noqa: E402
import museum_site.views  # noqa: E402
import museum_site.zeta_views  # noqa: E402


from museum_site.constants import (  # noqa: E402
    DETAIL_DOS,
    DETAIL_WIN16,
    DETAIL_WIN32,
    DETAIL_WIN64,
    DETAIL_LINUX,
    DETAIL_OSX,
    DETAIL_FEATURED,
    DETAIL_ZZM,
    DETAIL_GFX,
    DETAIL_MOD,
    DETAIL_SZZT,
    DETAIL_UTILITY,
    DETAIL_ZZT,
    DETAIL_ZIG,
    DETAIL_LOST,
    DETAIL_UPLOADED,
)

urlpatterns = [
    path("", museum_site.views.index, name="index"),
    path("credits/", museum_site.views.site_credits, name="credits"),
    path(
        "data-integrity/", museum_site.views.generic,
        {"template": "policy-data", "title": "Data Integrity"},
        name="data_integrity"),

    # Articles
    path(
        "article/categories", museum_site.article_views.article_categories,
        name="article_categories"),
    path(
        "article/search", museum_site.search_views.article_search,
        name="article_search"),
    path(
        "article/",
        museum_site.article_views.article_directory, name="article_directory"),
    path(
        "article/<slug:category>",
        museum_site.article_views.article_directory, name="article_category"),
    url(
        r"^article/(?P<article_id>[0-9]+)/page/(?P<page>[0-9]+)/(.*)$",
        museum_site.article_views.article_view, name="article_view_page"),
    url(
        r"^article/(?P<article_id>[0-9]+)/(.*)$",
        museum_site.article_views.article_view, {"page": 1},
        name="article_view"),

    # Special Article Pages (those with urls besides /article/#/title)
    path(
        "about-zzt/", museum_site.article_views.article_view,
        {"article_id": 534}, name="about_zzt"),
    path(
        "ascii/", museum_site.article_views.article_view, {"article_id": 3},
        name="ascii"),
    path(
        "clones/", museum_site.article_views.article_view, {"article_id": 6},
        name="clones"),
    path(
        "zzt-cheats/", museum_site.article_views.article_view,
        {"article_id": 22}, name="zzt_cheats"),
    path(
        "getting-started/", museum_site.article_views.article_view,
        {"article_id": 5}, name="zzt_dosbox"),
    path(
        "support/", museum_site.article_views.article_view,
        {"article_id": 586},
        name="support"),
    path(
        "zzt/", museum_site.article_views.article_view, {"article_id": 2},
        name="zzt_dl"),
    path(
        "zeta/", museum_site.article_views.article_view, {"article_id": 399},
        name="zeta"),

    # Collections
    path(
        "collection/play/", museum_site.views.play_collection,
        name="play_collection"),

    # Closer Looks
    path(
        "closer-looks/", museum_site.article_views.article_directory,
        {"category": "Closer Look"}, name="closer_looks"),
    path(
        "livestreams/", museum_site.article_views.article_directory,
        {"category": "Livestream"}, name="livestreams"),

    # Directories
    url(
        r"^directory/(?P<category>[a-z].*)$", museum_site.views.directory,
        name="directory"),

    # Exhibit
    url(
        r"^exhibit/(?P<letter>[a-z1!])/(?P<filename>.*)$",
        museum_site.views.exhibit,
        name="exhibit"),
    url(
        r"^exhibit/(?P<letter>[a-z1!])/(?P<filename>.*)/(?P<section>.*)$",
        museum_site.views.exhibit, name="exhibit-section"),

    # Files
    url(
        r"^article/(?P<letter>[a-z1!])/(?P<filename>.*)$",
        museum_site.file_views.file_articles,
        name="article"),
    path("browse/", museum_site.file_views.file_directory, name="browse"),
    url(
        r"^browse/(?P<letter>[a-z1])$", museum_site.file_views.file_directory,
        name="browse_letter"),
    url(
        r"^file/(?P<letter>[a-z1!])/(?P<filename>.*)$",
        museum_site.file_views.file_viewer, name="file"),
    url(
        r"^play/(?P<letter>[a-z1!])/(?P<filename>.*)$",
        museum_site.zeta_views.zeta_launcher,
        {"components": ["credits", "controls", "instructions", "players"]},
        name="play"),
    path(
        "file/local/", museum_site.file_views.file_viewer,
        {"local": True, "letter": "!", "filename": ""}, name="local_file"),

    # Files (alternate categories)
    path(
        "zzt-worlds/", museum_site.file_views.file_directory,
        {"details": [DETAIL_ZZT]}, name="zzt_worlds"),
    path(
        "super-zzt/", museum_site.file_views.file_directory,
        {"details": [DETAIL_SZZT]}, name="szzt_worlds"),
    path(
        "utilities/", museum_site.file_views.file_directory,
        {"details": [DETAIL_UTILITY], "show_description": True},
        name="utilities"),
    path(
        "zzm-audio/", museum_site.file_views.file_directory,
        {"details": [DETAIL_ZZM]}, name="zzm_audio"),
    path(
        "zig-worlds/", museum_site.file_views.file_directory,
        {"details": [DETAIL_ZIG]}, name="zig_worlds"),
    path(
        "modified-gfx/", museum_site.file_views.file_directory,
        {"details": [DETAIL_GFX]}, name="modified_gfx"),
    path(
        "modified-exe/", museum_site.file_views.file_directory,
        {"details": [DETAIL_MOD]}, name="modified_exe"),
    path(
        "osx/", museum_site.file_views.file_directory,
        {"details": [DETAIL_OSX]}, name="osx"),
    path(
        "linux/", museum_site.file_views.file_directory,
        {"details": [DETAIL_LINUX]}, name="linux"),
    path(
        "ms-dos/", museum_site.file_views.file_directory,
        {"details": [DETAIL_DOS]}, name="ms_dos"),
    path(
        "win16/", museum_site.file_views.file_directory,
        {"details": [DETAIL_WIN16]}, name="win16"),
    path(
        "win32/", museum_site.file_views.file_directory,
        {"details": [DETAIL_WIN32]}, name="win32"),
    path(
        "win64/", museum_site.file_views.file_directory,
        {"details": [DETAIL_WIN64]}, name="win64"),
    path(
        "lost-worlds/", museum_site.file_views.file_directory,
        {"details": [DETAIL_LOST]}, name="lost_worlds"),
    path(
        "uploaded/", museum_site.file_views.file_directory,
        {"details": [DETAIL_UPLOADED]}, name="uploaded_worlds"),
    path(
        "featured/", museum_site.file_views.file_directory,
        {
            "details": [DETAIL_FEATURED], "show_description": True,
            "show_featured": True
        },
        name="featured_games"),

    path("new/", museum_site.file_views.file_directory, name="new_files"),
    path(
        "new-releases/", museum_site.file_views.file_directory,
        name="new_releases"),

    # Help
    path(
        "help/genres/", museum_site.help_views.genres, name="help_genre"),

    # Mass Downloads
    path(
        "mass-downloads/", museum_site.views.mass_downloads,
        name="mass_downloads"),

    # Patrons Only
    path(
        "patron-articles/", museum_site.article_views.patron_articles,
        name="patron_articles"),

    # Policies
    path(
        "policy/correction/", museum_site.views.generic,
        {"template": "policy-correction", "title": "Correction Policy"},
        name="correction_policy"),
    path(
        "policy/removal/", museum_site.views.generic,
        {"template": "policy-removal", "title": "Removal Policy"},
        name="removal_policy"),
    path(
        "policy/review/", museum_site.views.generic,
        {"template": "policy-review", "title": "Review Policy"},
        name="review_policy"),
    path(
        "policy/upload/", museum_site.views.generic,
        {"template": "policy-upload", "title": "Upload Policy"},
        name="upload_policy"),

    # Random ZZT Worlds
    path("random/", museum_site.views.random, name="random"),
    path(
        "roulette/", museum_site.file_views.roulette,
        {"details": [DETAIL_ZZT]}, name="roulette"),

    # Reviews
    path(
        "review/", museum_site.review_views.review_directory,
        name="review_directory"),
    path(
        "review/<str:letter>/<str:filename>/",
        museum_site.file_views.review, name="reviews"),

    # Search
    path(
        "advanced-search/", museum_site.search_views.advanced_search,
        name="advanced_search"),
    path(
        "deep-search/", museum_site.search_views.deep_search,
        name="deep_search"),
    path("search/", museum_site.search_views.search, name="search"),

    # User
    path("user/login/", museum_site.user_views.login_user, name="login_user"),
    path(
        "user/logout/", museum_site.user_views.logout_user,
        name="logout_user"),
    path(
        "user/profile/<int:user_id>/<str:unused_slug>/",
        museum_site.user_views.user_profile, name="user_profile"),

    path(
        "user/profile/", museum_site.user_views.user_profile,
        name="my_profile"),
    path(
        "user/forgot-username/", museum_site.user_views.forgot_username,
        name="forgot_username"),
    path(
        "user/forgot-username/complete/", museum_site.user_views.user_profile,
        name="forgot_username_complete"),
    path(
        "user/forgot-password/", museum_site.user_views.forgot_password,
        name="forgot_password"),
    path(
        "user/reset-password/complete/", museum_site.views.generic,
        {
            "template": "user-reset-password-complete",
            "title": "Reset Password Complete"
        },
        name="reset_password_complete"),
    path(
        "user/reset-password/<str:token>/",
        museum_site.user_views.reset_password,
        name="reset_password_with_token"),
    path(
        "user/reset-password/", museum_site.user_views.reset_password,
        name="reset_password"),
    path(
        "user/activate-account/<str:token>/",
        museum_site.user_views.activate_account,
        name="activate_account_with_token"),
    path(
        "user/activate-account/", museum_site.user_views.activate_account,
        name="activate_account"),
    path(
        "user/resend-activation/",
        museum_site.user_views.resend_account_activation,
        name="resend_activation"),
    path(
        "user/change-char/", museum_site.user_views.change_char,
        name="change_char"),
    path(
        "user/change-email/", museum_site.user_views.change_email,
        name="change_email"),
    path(
        "user/change-password/", museum_site.user_views.change_password,
        name="change_password"),
    path(
        "user/change-username/", museum_site.user_views.change_username,
        name="change_username"),
    path(
        "user/change-patronage-visibility/",
        museum_site.user_views.change_patronage_visibility,
        name="change_patronage_visibility"),
    path(
        "user/change-pronouns/", museum_site.user_views.change_pronouns,
        name="change_pronouns"),
    path(
        "user/change-credit-preferences/",
        museum_site.user_views.change_credit_preferences,
        name="change_credit_preferences"),
    path(
        "error/login/", museum_site.user_views.error_login,
        name="error_login"),
    path(
        "error/registrations/", museum_site.user_views.error_registration,
        name="error_registration"),
    path(
        "error/password-reset/", museum_site.user_views.error_password_reset,
        name="error_password_reset"),

    # Worlds of ZZT
    path(
        "worlds-of-zzt/", museum_site.views.worlds_of_zzt_queue,
        name="worlds_of_zzt"),

    # Uploads
    path("upload/", museum_site.upload_views.upload, name="upload"),
    path(
        "upload/complete/", museum_site.upload_views.upload_complete,
        name="upload_complete"),

    # Zeta Live
    path("zeta-live/", museum_site.zeta_views.zeta_live),

    # AJAX
    path("ajax/deep-search/phase-<int:phase>/", museum_site.ajax.deep_search),
    path("ajax/get_zip_file/", museum_site.ajax.get_zip_file),
    path("ajax/wozzt_queue_add/", museum_site.ajax.wozzt_queue_add),
    path("ajax/render-review-text/", museum_site.ajax.render_review_text),

    # RSS
    path(
        "rss/", museum_site.views.generic,
        {"template": "rss-info", "title": "RSS Feeds"}, name="rss_feeds"),
    path(
        "rss/articles/", museum_site.feeds.LatestArticlesFeed(),
        name="rss_articles"),
    path(
        "rss/files/", museum_site.feeds.LatestFilesFeed(),
        name="rss_files"),
    path(
        "rss/reviews/", museum_site.feeds.LatestReviewsFeed(),
        name="rss_reviews"),
    path(
        "rss/uploads/", museum_site.feeds.LatestUploadsFeed(),
        name="rss_uploads"),

    # Redirects
    path(
        "twitter/", museum_site.views.redir,
        {"url": "https://twitter.com/worldsofzzt"}),
    path(
        "tumblr/", museum_site.views.redir,
        {"url": "http://worldsofzzt.tumblr.com"}),
    path(
        "discord/", museum_site.views.redir,
        {"url": "https://discordapp.com/invite/Nar4Upf"},
        name="discord_invite"),
    path(
        "patreon/", museum_site.views.redir,
        {"url": "https://patreon.com/worldsofzzt"}, name="patreon"),
    path(
        "youtube/", museum_site.views.redir,
        {"url": "https://www.youtube.com/c/WorldsofZZT"}),
    path(
        "twitch/", museum_site.views.redir,
        {"url": "https://twitch.tv/worldsofzzt"}),
    path(
        "github/", museum_site.views.redir,
        {"url": "https://github.com/DrDos0016/z2"}),

    # Tools
    path("tools/", museum_site.tool_views.tool_index, name="tool_index"),
    path(
        "tools/<int:pk>/", museum_site.tool_views.tool_list,
        name="tool_list"),
    path(
        "tools/add-livestream/<int:pk>/",
        museum_site.tool_views.add_livestream, name="add_livestream"),
    path(
        "tools/audit/zeta-config/", museum_site.tool_views.audit_zeta_config,
        name="audit_zeta_config"),
    path(
        "tools/extract-font/<int:pk>/",
        museum_site.tool_views.extract_font, name="extract_font"),
    path(
        "tools/log-viewer/", museum_site.tool_views.log_viewer,
        name="log_viewer"),
    path(
        "tools/mirror/<int:pk>/", museum_site.tool_views.mirror,
        name="mirror"),
    path(
        "tools/publish/<int:pk>/", museum_site.tool_views.publish,
        name="publish"),
    path(
        "tools/reletter/<int:pk>/", museum_site.tool_views.reletter,
        name="reletter"),
    path(
        "tools/replace_zip/<int:pk>/",
        museum_site.tool_views.replace_zip, name="replace_zip"),
    path("tools/scan/", museum_site.tool_views.scan, name="scan"),
    path(
        "tools/set_screenshot/<int:pk>/",
        museum_site.tool_views.set_screenshot, name="set_screenshot"),
    path(
        "tools/user-list/", museum_site.tool_views.user_list,
        name="user_list"),

    # Debug
    path("debug/", museum_site.debug_views.debug),
    path("debug/article/", museum_site.debug_views.debug_article),
    path("debug/colors/", museum_site.debug_views.debug_colors),
    path(
        "debug/forms/", museum_site.views.generic,
        {"template": "debug-forms", "title": "Form Debug"}),
    path("ajax/debug_file/", museum_site.ajax.debug_file),
]

if DEBUG:
    urlpatterns += static(
        "/zgames", document_root=os.path.join(BASE_DIR, "zgames")
    )
