import os

from django.views.generic.base import RedirectView
from django.urls import include, path

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
import museum_site.series_views  # noqa: E402
import museum_site.tool_views  # noqa: E402
import museum_site.user_views  # noqa: E402
import museum_site.upload_views  # noqa: E402
import museum_site.views  # noqa: E402
import museum_site.zeta_views  # noqa: E402

from museum_site.core.misc import legacy_redirect  # noqa: E402

urlpatterns = [
    path("", museum_site.views.index, name="index"),

    # /article/ -- Proper URLs
    path("article/",
         museum_site.article_views.article_directory,
         name="article_directory"),
    path("article/category/",
         museum_site.article_views.article_categories,
         name="article_categories"),
    path("article/category/<slug:category>/",
         museum_site.article_views.article_directory,
         name="article_category"),
    path("article/search/",
         museum_site.search_views.article_search,
         name="article_search"),
    path("article/view/<int:article_id>/page/<int:page>/<slug:slug>/",
         museum_site.article_views.article_view,
         name="article_view_page"),
    path("article/view/<int:article_id>/<slug:slug>/",
         museum_site.article_views.article_view,
         {"page": 1},
         name="article_view"),

    # /article/ -- Legacy Redirects
    path("article/categories/", legacy_redirect, {"name": "article_categories"}),
    path("article/<slug:category>/", legacy_redirect, {"name": "article_category"}),
    path("article/<int:article_id>/page/<int:page>/<slug:slug>/", legacy_redirect, {"name": "article_view_page"}),
    path("article/<int:article_id>/<slug:slug>/", legacy_redirect, {"name": "article_view"}),

    # Special Article Pages (those with urls besides /article/#/title)
    path("about-zzt/", museum_site.article_views.article_view,
         {"article_id": 534},
         name="about_zzt"),
    path("ascii/",
         museum_site.article_views.article_view,
         {"article_id": 3},
         name="ascii"),
    path("clones/",
         museum_site.article_views.article_view,
         {"article_id": 6},
         name="clones"),
    path("getting-started/",
         museum_site.article_views.article_view,
         {"article_id": 5},
         name="zzt_dosbox"),
    path("support/",
         museum_site.article_views.article_view,
         {"article_id": 576},
         name="support"),
    path("zeta/",
         museum_site.article_views.article_view,
         {"article_id": 399},
         name="zeta"),
    path("zzt/",
         museum_site.article_views.article_view,
         {"article_id": 2},
         name="zzt_dl"),
    path("zzt-cheats/",
         museum_site.article_views.article_view,
         {"article_id": 22},
         name="zzt_cheats"),

    # /detail/ -- Proper URLs
    path("detail/",
         museum_site.help_views.Detail_Overview_View.as_view(),
         name="file_details"),
    path("detail/view/<slug:slug>/",
         museum_site.file_views.files_by_detail,
         name="files_by_detail"),
    # /detail/ -- Legacy Redirects
    path("detail/<slug:slug>/", legacy_redirect, {"name": "files_by_detail"}),


    path("zzt-worlds/", legacy_redirect, {"name": "files_by_detail", "slug":"zzt-world"}, name="zzt_worlds"),
    path("super-zzt/", legacy_redirect, {"name": "files_by_detail", "slug":"super-zzt-world"}, name="szzt_worlds"),
    path("utilities/", legacy_redirect, {"name": "files_by_detail", "slug":"utility"}, name="utilities"),
    path("zzm-audio/", legacy_redirect, {"name": "files_by_detail", "slug":"zzm-audio"}, name="zzm_audio"),
    path("zig-worlds/", legacy_redirect, {"name": "files_by_detail", "slug":"zig-world"}, name="zig_worlds"),
    path("modified-gfx/", legacy_redirect, {"name": "files_by_detail", "slug":"modified-graphics"}, name="modified_gfx"),
    path("modified-exe/", legacy_redirect, {"name": "files_by_detail", "slug":"modified-executable"}, name="modified_exe"),
    path("ms-dos/", legacy_redirect, {"name": "files_by_detail", "slug":"ms-dos"}, name="ms_dos"),
    path("lost-worlds/", legacy_redirect, {"name": "files_by_detail", "slug":"lost-world"}, name="lost_worlds"),
    path("uploaded/", legacy_redirect, {"name": "files_by_detail", "slug":"uploaded"}, name="uploaded_worlds"),
    path("featured/", legacy_redirect, {"name": "files_by_detail", "slug":"featured-world"}, name="featured_games"),

    # Directories
    path("browse/", museum_site.file_views.file_directory, name="browse"),
    path(
        "browse/<str:letter>/", museum_site.file_views.file_directory,
        name="browse_letter"
    ),
    path(
        "genre/<str:genre>/", museum_site.file_views.file_directory,
        name="browse_genre"
    ),
    path(
        "directory/<slug:category>/", museum_site.views.directory,
        name="directory"),
    path("new/", museum_site.file_views.file_directory, name="new_files"),
    path(
        "new-releases/", museum_site.file_views.file_directory,
        name="new_releases"),
    path(
        "review/", museum_site.review_views.Review_Directory_View.as_view(),
        name="review_directory"),
    path(
        "review/author/", museum_site.review_views.Reviewer_Directory_View.as_view(),
        name="reviewer_directory"),
    path(
        "review/author/<str:author>/", museum_site.review_views.Review_Directory_View.as_view(),
        name="reviews_by_author"),
    path(
        "review/search/", museum_site.review_views.Review_Directory_View.as_view(),
        name="review_search"),
    path(
        "series/", museum_site.series_views.Series_Directory_View.as_view(),
        name="series_directory"),

    # ZFiles
    path(
        "article/<str:letter>/<str:key>/",
        museum_site.file_views.file_articles,
        name="article"
    ),
    path(
        "attributes/<str:letter>/<str:key>/",
        museum_site.file_views.file_attributes, name="file_attributes"),
    path(
        "download/<str:letter>/<str:key>/",
        museum_site.file_views.file_download, name="file_download"),
    path(
        "file/local/", museum_site.file_views.file_viewer,
        {"local": True, "letter": "!", "key": ""}, name="local_file"),
    path(
        "file/<str:letter>/<str:key>/",
        museum_site.file_views.file_viewer, name="file"),
    path(
        "pk/<int:pk>/",
        museum_site.file_views.get_file_by_pk, name="get_file_by_pk"),
    path(
        "play/<str:letter>/<str:key>/",
        museum_site.zeta_views.zeta_launcher,
        {"components": ["credits", "controls", "instructions", "players"]},
        name="play"),
    path(
        "review/<str:letter>/<str:key>/",
        museum_site.file_views.review, name="reviews"),

    # Help
    path("help/", RedirectView.as_view(url="/article/help/")),
    path("help/detail/", museum_site.help_views.Detail_Overview_View.as_view(), name="help_detail"),
    path("help/genre/", museum_site.help_views.Genre_Overview_View.as_view(), name="help_genre"),
    path("help/zfile/", museum_site.help_views.zfiles, name="help_zfiles"),

    # Special Pages
    path("explicit-warning/", museum_site.views.explicit_warning, name="explicit_warning"),
    path(
        "discord/", museum_site.views.discord_overview, name="discord"),
    path("credits/", museum_site.views.site_credits, name="credits"),
    path(
        "mass-downloads/", museum_site.views.mass_downloads,
        name="mass_downloads"),
    path(
        "patron-articles/", museum_site.article_views.patron_articles,
        name="patron_articles"),

    # Policies
    path(
        "policy/data-integrity/", museum_site.views.generic,
        {"template": "policy-data", "title": "Data Integrity"},
        name="data_integrity"),
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
        "roulette/", museum_site.file_views.file_directory, name="roulette"
    ),

    # Series
    path(
        "series/<int:series_id>/<slug:slug>/",
        museum_site.series_views.Series_Overview_View.as_view(),
        name="series_overview"),

    # Search
    path(
        "advanced-search/", museum_site.search_views.advanced_search,
        name="advanced_search"),
    path("search/", museum_site.file_views.file_directory, name="search"),

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
            "template": "user/reset-password-complete",
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
        "user/change-patron-email/",
        museum_site.user_views.change_patron_email,
        name="change_patron_email"),
    path(
        "user/change-username/", museum_site.user_views.change_username,
        name="change_username"),
    path(
        "user/change-pronouns/", museum_site.user_views.change_pronouns,
        name="change_pronouns"),
    path(
        "error/login/", museum_site.user_views.error_login,
        name="error_login"),
    path(
        "error/registrations/", museum_site.user_views.error_registration,
        name="error_registration"),
    path(
        "error/password-reset/", museum_site.user_views.error_password_reset,
        name="error_password_reset"),
    path(
        "user/update-tos/",
        museum_site.user_views.update_tos,
        name="update_tos"),
    path(
        "user/manage-saved-data/", museum_site.user_views.manage_saved_data,
        name="manage_saved_data"),

    # User Patron Pages
    path(
        "user/change-credit-preferences/",
        museum_site.user_views.change_credit_preferences,
        name="change_credit_preferences"),
    path(
        "user/change-patronage-visibility/",
        museum_site.user_views.change_patronage_visibility,
        name="change_patronage_visibility"),
    path(
        "user/change-stream-poll-nominations/",
        museum_site.user_views.change_patron_perks,
        name="change_stream_poll_nominations"),
    path(
        "user/change-stream-selections/",
        museum_site.user_views.change_patron_perks,
        name="change_stream_selections"),
    path(
        "user/change-closer-look-poll-nominations/",
        museum_site.user_views.change_patron_perks,
        name="change_closer_look_poll_nominations"),
    path(
        "user/change-guest-stream-selections/",
        museum_site.user_views.change_patron_perks,
        name="change_guest_stream_selections"),
    path(
        "user/change-closer-look-selections/",
        museum_site.user_views.change_patron_perks,
        name="change_closer_look_selections"),
    path(
        "user/change-bkzzt-topics/",
        museum_site.user_views.change_patron_perks,
        name="change_bkzzt_topics"),

    # Worlds of ZZT
    path(
        "worlds-of-zzt/", museum_site.views.worlds_of_zzt_queue,
        name="worlds_of_zzt"),

    # Uploads
    path("upload/", museum_site.upload_views.upload, name="upload"),
    path(
        "upload/complete/<str:token>/",
        museum_site.upload_views.upload_complete,
        name="upload_complete"
    ),
    path(
        "upload/delete/", museum_site.upload_views.upload_delete,
        name="upload_delete"
    ),
    path(
        "upload/delete/complete/", museum_site.views.generic,
        {"template": "upload-delete-complete", "title": "Upload Deleted"},
        name="upload_delete_complete",
    ),
    path(
        "upload/edit/", museum_site.upload_views.upload_edit,
        name="upload_edit"),

    # Zeta Live
    path("zeta-live/", museum_site.zeta_views.zeta_live),

    # AJAX
    path(
        "ajax/get-author-suggestions/", museum_site.ajax.get_author_suggestions
    ),
    path(
        "ajax/get-company-suggestions/",
        museum_site.ajax.get_company_suggestions
    ),
    path("ajax/get_zip_file/", museum_site.ajax.get_zip_file),
    path(
        "ajax/get-search-suggestions/", museum_site.ajax.get_search_suggestions
    ),
    path("ajax/render-review-text/", museum_site.ajax.render_review_text),
    path("ajax/wozzt_queue_add/", museum_site.ajax.wozzt_queue_add),

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

    # Non-Museum Websites
    path(
        "twitter/", RedirectView.as_view(url="https://twitter.com/worldsofzzt"),
    ),
    path(
        "tumblr/", RedirectView.as_view(url="http://worldsofzzt.tumblr.com"),
    ),
    path(
        "patreon/", RedirectView.as_view(url="https://patreon.com/worldsofzzt"),
        name="patreon"),
    path(
        "youtube/", RedirectView.as_view(
            url="https://www.youtube.com/c/WorldsofZZT"),
        ),
    path(
        "twitch/", RedirectView.as_view(url="https://twitch.tv/worldsofzzt"),
        ),
    path(
        "github/", RedirectView.as_view(
            url="https://github.com/DrDos0016/museum-of-zzt"
            ),
        ),

    # Legacy Redirects
    path(
        "closer-looks/", RedirectView.as_view(url="/article/closer-look/")),
    path(
        "livestreams/", RedirectView.as_view(url="/article/livestream/")),
    path(
        "data-integrity/", RedirectView.as_view(url="/policy/data-integrity/")),

    # Tools
    path("tools/", museum_site.tool_views.tool_index, name="tool_index"),
    path(
        "tools/add-livestream/<int:pk>/",
        museum_site.tool_views.add_livestream, name="add_livestream"),
    path(
        "tools/audit/genres/", museum_site.tool_views.audit_genres,
        name="audit_genres"),
    path(
        "tools/audit/scrolls/", museum_site.tool_views.audit_scrolls,
        name="audit_scrolls"),
    path(
        "tools/audit/zeta-config/", museum_site.tool_views.audit_zeta_config,
        name="audit_zeta_config"),
    path(
        "tools/crediting-preferences/",
        museum_site.tool_views.crediting_preferences,
        name="crediting_preferences"),
    path(
        "tools/extract-font/<int:pk>/",
        museum_site.tool_views.extract_font, name="extract_font"),
    path(
        "tools/log-viewer/", museum_site.tool_views.log_viewer,
        name="log_viewer"),
    path(
        "tools/manage-details/<str:letter>/<str:filename>/",
        museum_site.tool_views.manage_details,
        name="manage_details"
    ),
    path(
        "tools/mirror/<str:letter>/<str:filename>/",
        museum_site.tool_views.mirror,
        name="mirror"
    ),
    path(
        "tools/patron-article-rotation/",
        museum_site.tool_views.patron_article_rotation,
        name="patron_article_rotation"),
    path(
        "tools/patron-input/", museum_site.tool_views.patron_input,
        name="patron_input"),
    path(
        "tools/prep-publication-pack/",
        museum_site.tool_views.prep_publication_pack,
        name="prep_publication_pack"),
    path(
        "tools/pub-pack-file-assocs/",
        museum_site.tool_views.publication_pack_file_associations,
        name="pub_pack_file_assocs"),
    path(
        "tools/publish/<int:pk>/", museum_site.tool_views.publish,
        name="publish"),
    path(
        "tools/review-approvals/", museum_site.tool_views.review_approvals,
        name="review_approvals"),
    path(
        "tools/reletter/<int:pk>/", museum_site.tool_views.reletter,
        name="reletter"),
    path(
        "tools/replace_zip/<int:pk>/",
        museum_site.tool_views.replace_zip, name="replace_zip"),
    path("tools/scan/", museum_site.tool_views.scan, name="musuem_scan"),
    path("tools/series/add/", museum_site.tool_views.series_add,
         name="series_add"),
    path(
        "tools/set_screenshot/<int:pk>/",
        museum_site.tool_views.set_screenshot, name="set_screenshot"),
    path("tools/stream-card/", museum_site.tool_views.stream_card,
         name="stream_card"),
    path(
        "tools/user-list/", museum_site.tool_views.user_list,
        name="user_list"),
    path(
        "tools/<str:letter>/<str:filename>/",
        museum_site.tool_views.tool_index,
        name="tool_index_with_file"
    ),

    # Debug
    path("debug/", museum_site.debug_views.debug),
    path("debug/<str:filename>.html", museum_site.debug_views.debug),
    path("debug/article/<str:fname>/", museum_site.debug_views.debug_article),
    path("debug/article/", museum_site.debug_views.debug_article),
    path("debug/colors/", museum_site.debug_views.debug_colors),
    path(
        "debug/forms/", museum_site.views.generic,
        {"template": "debug-forms", "title": "Form Debug"}),
    path("ajax/debug_file/", museum_site.ajax.debug_file),
    path(
        "debug/advanced-search/", museum_site.debug_views.debug_advanced_search
    ),
]

if DEBUG:
    urlpatterns += static(
        "/zgames", document_root=os.path.join(BASE_DIR, "zgames")
    )
