import os

from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView
from django.urls import include, path
from django.shortcuts import redirect

from museum.settings import BASE_DIR, DEBUG
if DEBUG:
    from django.conf.urls.static import static

import museum_site.ajax  # noqa: E402
import museum_site.article_views  # noqa: E402
import museum_site.collection_views  # noqa: E402
import museum_site.debug_views  # noqa: E402
import museum_site.file_views  # noqa: E402
import museum_site.generic_model_views  # noqa: E402
import museum_site.feeds  # noqa: E402
import museum_site.help_views  # noqa: E402
import museum_site.review_views  # noqa: E402
import museum_site.scroll_views  # noqa: E402
import museum_site.series_views  # noqa: E402
import museum_site.tool_views  # noqa: E402
import museum_site.user_views  # noqa: E402
import museum_site.upload_views  # noqa: E402
import museum_site.views  # noqa: E402
import museum_site.zeta_views  # noqa: E402

from museum_site.core.misc import legacy_redirect  # noqa: E402

urlpatterns = [
    path("", museum_site.views.index, name="index"),

    # /action/
    path("action/set-setting/", museum_site.views.set_setting, name="action_set_setting"),
    path("action/close-tool/", museum_site.views.close_tool, name="action_close_tool"),
    path("action/staff/add-zfile-assocs/", museum_site.views.add_zfile_assocs, name="action_staff_add_zfile_assocs"),

    # /ajax/
    path("ajax/submit-form/<slug:slug>/", museum_site.ajax.submit_form, name="ajax_submit_form"),
    path("ajax/fetch-zip-content/", museum_site.ajax.fetch_zip_content, name="ajax_fetch_zip_content"),
    path("ajax/fetch-zip-info/", museum_site.ajax.fetch_zip_info, name="ajax_fetch_zip_info"),
    path("ajax/get-search-suggestions/", museum_site.ajax.get_search_suggestions, name="ajax_get_search_suggestions"),
    path("ajax/get-stream-entries/", museum_site.ajax.get_stream_entries, name="ajax_get_stream_entries"),
    path("ajax/get-stream-schedule/", museum_site.ajax.qad_get_stream_schedule, name="ajax_get_stream_schedule"),
    path("ajax/get-<str:field>-suggestions/", museum_site.ajax.get_suggestions_for_field, name="ajax_get_suggestions_for_field"),
    path("ajax/get_zip_file/", museum_site.ajax.get_zip_file, name="ajax_get_zip_file"),
    path("ajax/get-zip-file-by-key/", museum_site.ajax.get_zip_file_by_key, name=""),
    path("ajax/render-review-text/", museum_site.ajax.render_review_text, name="ajax_render_review_text"),
    path("ajax/wozzt_queue_add/", museum_site.ajax.wozzt_queue_add, name="ajax_wozzt_queue_add"),

    path("ajax/collection/arrange-collection/", museum_site.ajax.arrange_collection, name="ajax_collection_arrange"),
    path("ajax/collection/get-collection-addition/", museum_site.ajax.get_collection_addition, name="ajax_collection_get_addition"),
    path("ajax/collection/remove-from-collection/", museum_site.ajax.remove_from_collection, name="ajax_collection_remove"),
    path("ajax/collection/update-collection-entry/", museum_site.ajax.update_collection_entry, name="ajax_collection_update"),
    path("ajax/collection/get-available-collections/", museum_site.ajax.otf_get_available_collections, name="ajax_otf_get_collections"),

    # /article/
    path("article/",  RedirectView.as_view(pattern_name="article_browse", permanent=True)),
    path("article/browse/", museum_site.article_views.Article_List_View.as_view(), name="article_browse"),
    path("article/browse/category/", museum_site.article_views.Article_Categories_List_View.as_view(), name="article_browse_categories"),
    path("article/browse/category/<slug:category_slug>/", museum_site.article_views.Article_List_View.as_view(), name="article_browse_category"),
    path("article/search/", museum_site.article_views.Article_Search_View.as_view(), name="article_search"),
    path("article/view/<int:pk>/", museum_site.article_views.redirect_with_slug, name="article_view_slugless"),
    path("article/view/<int:pk>/page/<int:page>/<slug:slug>/", museum_site.article_views.Article_Detail_View.as_view(), name="article_view_page"),
    path("article/view/<int:pk>/<slug:slug>/", museum_site.article_views.Article_Detail_View.as_view(), {"page": 1}, name="article_view"),
    path("article/lock/<int:article_id>/<slug:slug>/", museum_site.article_views.article_lock, name="article_lock"),

    # /article/ -- Legacy Redirects
    path("article/category/", RedirectView.as_view(pattern_name="article_browse_categories", permanent=True)),
    path("article/category/<slug:category_slug>/", RedirectView.as_view(pattern_name="article_browse_category", permanent=True)),
    path("article/categories/", legacy_redirect, {"name": "article_browse_categories"}),
    path("article/<slug:category_slug>/", legacy_redirect, {"name": "article_browse_category"}),
    path("article/<int:pk>/page/<int:page>/<slug:slug>/", legacy_redirect, {"name": "article_view_page"}),
    path("article/<int:pk>/<slug:slug>/", legacy_redirect, {"name": "article_view"}),
    path("closer-looks/", legacy_redirect, {"name": "article_browse_category", "category_slug": "closer-look"}),
    path("livestreams/", legacy_redirect, {"name": "article_browse_category", "category_slug": "livestream"}),

    # Article Shortcut URLs
    path("about-zzt/", RedirectView.as_view(pattern_name="article_view"), {"pk": 534, "slug": "about-zzt"}, name="about_zzt"),
    path("clones/", RedirectView.as_view(pattern_name="article_view"), {"pk": 6, "slug": "zzt-clones"}, name="clones"),
    path("getting-started/", RedirectView.as_view(pattern_name="article_view"), {"pk": 5, "slug": "getting-started-with-zzt"}, name="zzt_dosbox"),
    path("support/", RedirectView.as_view(pattern_name="article_view"), {"pk": 576, "slug": "supporting-the-worlds-of-zzt-project"}, name="support"),
    path("zeta/", RedirectView.as_view(pattern_name="article_view"), {"pk": 399, "slug": "zzting-with-zeta"}, name="zeta"),
    path("zzt/", RedirectView.as_view(pattern_name="article_view"), {"pk": 1176, "slug": "zzt-versions"}, name="zzt_dl"),
    path("zzt-cheats/", RedirectView.as_view(pattern_name="article_view"), {"pk": 22, "slug": "zzt-cheats"}, name="zzt_cheats"),

    # /collection/
    path("collection/", RedirectView.as_view(pattern_name="collection_browse", permanent=True)),
    path("collection/browse/", museum_site.collection_views.Collection_List_View.as_view(), name="collection_browse"),
    path("collection/delete/<slug:slug>/", login_required(museum_site.collection_views.Collection_Delete_View.as_view()), name="collection_delete"),
    path("collection/edit/<slug:slug>/", login_required(museum_site.collection_views.Collection_Update_View.as_view()), name="collection_edit"),
    path(
        "collection/manage-contents/<slug:slug>/",
        login_required(museum_site.collection_views.Collection_Manage_Contents_View.as_view()), name="collection_manage_contents"
    ),
    path("collection/new/", login_required(museum_site.collection_views.Collection_Create_View.as_view()), name="collection_new"),
    path("collection/on-the-fly-collections/", museum_site.collection_views.On_The_Fly_Collections_View.as_view(), name="collection_on_the_fly_collections"),
    path("collection/view/<slug:collection_slug>/", museum_site.collection_views.Collection_Contents_View.as_view(), name="collection_view"),
    path("collection/user/", login_required(museum_site.collection_views.Collection_List_View.as_view()), name="collection_user"),

    # /company/
    path("company/view/<slug:slug>/", museum_site.views.Company_Overview_View.as_view(), name="company_view"),

    # /debug/
    path("debug/", museum_site.debug_views.debug),
    path("debug/error/<int:status_code>/", museum_site.debug_views.error_status_test),
    path("debug/blank/", museum_site.debug_views.debug_blank),
    path("debug/<str:filename>.html", museum_site.debug_views.debug),
    path("debug/article/<str:fname>/", museum_site.debug_views.debug_article, name="debug_article"),
    path("debug/article/", museum_site.debug_views.debug_article),
    path("debug/form-elements/", museum_site.debug_views.debug_form_elements),
    path("debug/play/", museum_site.debug_views.debug_play),
    path("debug/solo/", museum_site.debug_views.debug_solo),
    path("debug/widgets/", museum_site.debug_views.debug_widgets),
    path("debug/attrs/<str:key>/", museum_site.debug_views.debug_attrs),

    # /detail/
    path("detail/browse/", museum_site.help_views.Detail_Overview_View.as_view(), name="detail_browse"),

    # /detail/ -- Legacy Redirects
    path("detail/", RedirectView.as_view(pattern_name="detail_browse", permanent=True)),
    path("detail/view/<slug:detail_slug>/", legacy_redirect, {"name": "zfile_browse_field"}),
    path("detail/<slug:detail_slug>/", legacy_redirect, {"name": "zfile_browse_field"}),
    path("zzt-worlds/", legacy_redirect, {"name": "files_by_detail", "detail_slug": "zzt-world"}, name="zzt_worlds"),
    path("super-zzt/", legacy_redirect, {"name": "files_by_detail", "detail_slug": "super-zzt-world"}, name="szzt_worlds"),
    path("utilities/", legacy_redirect, {"name": "files_by_detail", "detail_slug": "utility"}, name="utilities"),
    path("zzm-audio/", legacy_redirect, {"name": "files_by_detail", "detail_slug": "zzm-audio"}, name="zzm_audio"),
    path("zig-worlds/", legacy_redirect, {"name": "files_by_detail", "detail_slug": "zig-world"}, name="zig_worlds"),
    path("modified-gfx/", legacy_redirect, {"name": "files_by_detail", "detail_slug": "modified-graphics"}, name="modified_gfx"),
    path("modified-exe/", legacy_redirect, {"name": "files_by_detail", "detail_slug": "modified-executable"}, name="modified_exe"),
    path("ms-dos/", legacy_redirect, {"name": "files_by_detail", "detail_slug": "ms-dos"}, name="ms_dos"),
    path("lost-worlds/", legacy_redirect, {"name": "files_by_detail", "detail_slug": "lost-world"}, name="lost_worlds"),
    path("uploaded/", legacy_redirect, {"name": "zfile_browse_field", "field": "detail", "value": "uploaded"}, name="uploaded_worlds"),
    path("featured/", legacy_redirect, {"name": "zfile_browse_field", "field": "detail", "value": "featured-world"}, name="featured_games"),

    # /file/
    path("file/", RedirectView.as_view(pattern_name="zfile_browse", permanent=True)),
    path("file/browse/", museum_site.file_views.ZFile_List_View.as_view(), name="zfile_browse"),
    path("file/browse/new-finds/", museum_site.file_views.ZFile_List_View.as_view(), name="zfile_browse_new_finds"),
    path("file/browse/new-releases/", museum_site.file_views.ZFile_List_View.as_view(), name="zfile_browse_new_releases"),
    path("file/browse/<str:letter>/", museum_site.file_views.ZFile_List_View.as_view(), name="zfile_browse_letter"),
    path("file/browse/<str:field>/<path:value>/", museum_site.file_views.ZFile_List_View.as_view(), name="zfile_browse_field"),
    path("file/random/", museum_site.views.random, name="zfile_random"),
    path("file/roulette/", museum_site.file_views.prepare_roulette, name="zfile_roulette"),
    path("file/search/", museum_site.file_views.ZFile_Search_View.as_view(), name="zfile_search"),
    path("file/mass-downloads/", museum_site.views.mass_downloads, name="zfile_mass_downloads"),
    path("file/article/<str:key>/", museum_site.file_views.ZFile_Article_List_View.as_view(), name="zfile_article"),
    path("file/attribute/<str:key>/", museum_site.file_views.file_attributes, name="zfile_attribute"),
    path("file/download/<str:key>/", museum_site.file_views.file_download, name="zfile_download"),
    path("file/review/<str:key>/", museum_site.file_views.ZFile_Review_List_View.as_view(), name="zfile_review"),
    path("file/view-local/", museum_site.file_views.file_viewer, {"local": True, "key": ""}, name="zfile_view_local"),
    path("file/view-local/beta", museum_site.file_views.file_viewer_new, {"local": True, "key": ""}, name="zfile_view_local_beta"),
    path("file/view/<str:key>/", museum_site.file_views.file_viewer, name="file"),
    path("file/view/<str:key>/beta/", museum_site.file_views.file_viewer_new, name="file_beta"),
    path("file/pk/<int:pk>/", museum_site.file_views.get_file_by_pk, name="zfile_pk"),
    path("file/play/<str:key>/", museum_site.zeta_views.zeta_launcher, {"components": ["credits", "controls", "instructions", "players"]}, name="zfile_play"),
    #path("file/play/<str:key>/", museum_site.zeta_views.Zeta_Launcher_View.as_view(), name="zfile_play"),
    # /file/ -- Legacy Redirects
    path("random/", legacy_redirect, {"name": "zfile_random"}),
    path("roulette/", legacy_redirect, {"name": "zfile_roulette"}),
    path("search/", legacy_redirect, {"name": "zfile_search"}),
    path("advanced-search/", legacy_redirect, {"name": "zfile_search"}),
    path("file/advanced-search/", RedirectView.as_view(pattern_name="zfile_search", permanent=True)),
    path("mass-downloads/", legacy_redirect, {"name": "zfile_mass_downloads"}),
    path("article/<str:letter>/<str:key>/", legacy_redirect, {"name": "zfile_article", "strip": ["letter"]}),
    path("attributes/<str:letter>/<str:key>/", legacy_redirect, {"name": "zfile_attribute", "strip": ["letter"]}),
    path("download/<str:letter>/<str:key>/", legacy_redirect, {"name": "zfile_download", "strip": ["letter"]}),
    path("file/local/", legacy_redirect, {"name": "zfile_view_local"}),
    path("file/<str:letter>/<str:key>/", legacy_redirect, {"name": "file", "strip": ["letter"]}),
    path("pk/<int:pk>/", legacy_redirect, {"name": "zfile_pk"}),
    path("play/<str:letter>/<str:key>/", legacy_redirect, {"name": "zfile_play", "strip": ["letter"]}),
    # More at the end of the list...

    # /follow/
    path("follow/", museum_site.views.follow, name="follow"),

    # /genre/
    path("genre/browse/", museum_site.help_views.Genre_Overview_View.as_view(), name="genre_browse"),
    # /genre/ -- Legacy Redirects
    path("genre/", RedirectView.as_view(pattern_name="genre_browse", permanent=True)),
    path("genre/<slug:genre_slug>/", legacy_redirect, {"name": "zfile_browse_field"}),

    # /help/
    path("help/", RedirectView.as_view(url="/article/help/")),
    path("help/detail/", museum_site.help_views.Detail_Overview_View.as_view(), name="help_detail"),
    path("help/genre/", museum_site.help_views.Genre_Overview_View.as_view(), name="help_genre"),
    path("help/zfile/", museum_site.help_views.zfiles, name="help_zfile"),

    # /policy/
    path("policy/<slug:slug>/", museum_site.views.Policy_View.as_view(), name="policy"),

    # /policy/ -- Legacy Redirects
    path("data-integrity/", RedirectView.as_view(url="/policy/data-integrity/", permanent=True)),

    # /review/
    path("feedback/edit/<int:pk>/", museum_site.review_views.Feedback_Edit_View.as_view(), name="feedback_edit"),
    path("feedback/delete/confirm/", museum_site.review_views.Feedback_Delete_Confirmation_View.as_view(), name="feedback_delete_confirm"),
    path("review/", RedirectView.as_view(pattern_name="review_browse", permanent=True)),
    path("review/browse/", museum_site.review_views.Review_List_View.as_view(), name="review_browse"),
    path("review/browse/author/", museum_site.review_views.Reviewer_Directory_View.as_view(), name="review_browse_authors"),
    path("review/browse/author/<str:author>/", museum_site.review_views.Review_List_View.as_view(), name="review_browse_author"),
    path("review/search/", museum_site.review_views.Feedback_Search_View.as_view(), name="review_search"),
    # /review/ -- Legacy Redirects
    path("review/author/", RedirectView.as_view(pattern_name="review_browse_authors", permanent=True)),
    path("review/author/<str:author>/", RedirectView.as_view(pattern_name="review_browse_author", permanent=True)),

    # /rss/
    path("rss/", museum_site.views.RSS_View.as_view(), name="rss"),
    path("rss/articles/", museum_site.feeds.Latest_Articles_Feed(), name="rss_articles"),
    path("rss/articles/upcoming/", museum_site.feeds.Upcoming_Articles_Feed(), name="rss_articles_upcoming"),
    path("rss/articles/unpublished/", museum_site.feeds.Unpublished_Articles_Feed(), name="rss_articles_unpublished"),
    path("rss/files/", museum_site.feeds.Latest_Files_Feed(), name="rss_files"),
    path("rss/reviews/", museum_site.feeds.Latest_Reviews_Feed(), name="rss_reviews"),
    path("rss/uploads/", museum_site.feeds.Latest_Uploads_Feed(), name="rss_uploads"),

    # /scroll/
    path("scroll/", RedirectView.as_view(pattern_name="scroll_browse", permanent=True)),
    path("scroll/browse/", museum_site.scroll_views.Scroll_List_View.as_view(), name="scroll_browse"),
    path("scroll/<slug:navigation>/", museum_site.scroll_views.scroll_navigation, name="scroll_navigation"),
    path("scroll/view/<int:pk>/", museum_site.scroll_views.Scroll_Detail_View.as_view()),
    path("scroll/view/<int:pk>/<slug:slug>/", museum_site.scroll_views.Scroll_Detail_View.as_view(), name="scroll_view"),

    # /series/
    path("series/browse/", museum_site.series_views.Series_List_View.as_view(), name="series_browse"),
    path("series/view/<int:series_id>/<slug:slug>/", museum_site.series_views.Series_Contents_View.as_view(), name="series_view"),
    # /series/ -- Legacy Redirects
    path("series/", RedirectView.as_view(pattern_name="series_browse", permanent=True)),
    path("series/<int:series_id>/<slug:slug>/", RedirectView.as_view(pattern_name="series_view", permanent=True)),

    # /tool/
    # path("tool/tinyzoo-converter/", museum_site.tool_views.tinyzoo_converter, name="tinyzoo_converter"),

    # /tools/ -- THESE WILL BE RENAMED FOR STAFF
    path("tools/", museum_site.tool_views.tool_index, name="tool_index"),
    path("tools/add-livestream/<str:key>/", museum_site.tool_views.add_livestream, name="add_livestream"),
    path("tools/audit/colors/", museum_site.tool_views.audit_colors, name="audit_colors"),
    path("tools/audit/settings/", museum_site.tool_views.audit_settings, name="audit_settings"),
    path("tools/audit/<str:target>/", museum_site.tool_views.audit, name="audit"),
    path("tools/compare-checksums/", museum_site.tool_views.compare_checksums, name="compare_checksums"),
    path("tools/discord-announcement/", museum_site.tool_views.discord_announcement, name="tool_discord_announcement"),
    path("tools/extract-font/<str:key>/", museum_site.tool_views.extract_font, name="extract_font"),
    path("tools/empty-upload-queue/", museum_site.tool_views.empty_upload_queue, name="empty_upload_queue"),
    path("tools/feedback-approvals/", museum_site.tool_views.feedback_approvals, name="feedback_approvals"),
    path("tools/feedback-approvals/delete/", museum_site.tool_views.feedback_approvals_delete, name="feedback_approvals_delete"),
    path("tools/video-description-generator/", museum_site.tool_views.video_description_generator, name="video_description_generator"),
    path("tools/log-viewer/", museum_site.tool_views.log_viewer, name="log_viewer"),
    path("tools/manage-cache/", museum_site.tool_views.manage_cache, name="manage_cache"),
    path("tools/manage-downloads/<str:key>/", museum_site.tool_views.manage_downloads, name="tool_manage_downloads"),
    path("tools/manage-details/<str:key>/", museum_site.tool_views.publish, {"mode": "MANAGE"}, name="manage_details"),
    path("tools/mirror/<str:key>/", museum_site.tool_views.mirror, name="mirror"),
    path("tools/month-in-review/", museum_site.tool_views.month_in_review, name="month_in_review"),
    path("tools/orphaned-objects/", museum_site.tool_views.orphaned_objects, name="orphaned_objects"),
    path("tools/patron-article-rotation/", museum_site.tool_views.patron_article_rotation, name="patron_article_rotation"),
    path("tools/patron-input/", museum_site.tool_views.patron_input, name="patron_input"),
    path("tools/prep-publication-pack/", museum_site.tool_views.prep_publication_pack, name="prep_publication_pack"),
    path("tools/publish/<str:key>/", museum_site.tool_views.publish, name="publish"),
    path("tools/reletter/<str:key>/", museum_site.tool_views.reletter, name="reletter"),
    path("tools/replace_zip/<str:key>/", museum_site.tool_views.replace_zip, name="replace_zip"),
    path("tools/scan/", museum_site.tool_views.scan, name="museum_scan"),
    path("tools/series/add/", museum_site.tool_views.series_add, name="series_add"),
    path("tools/set_screenshot/<str:key>/", museum_site.tool_views.set_screenshot, name="set_screenshot"),
    path("tools/stream-vod-thumbnail-generator/", museum_site.tool_views.stream_vod_thumbnail_generator, name="tool_stream_vod_thumbnail_generator"),
    path("tools/<str:key>/", museum_site.tool_views.tool_index, name="tool_index_with_file"),

    # /upload/
    path("upload/", museum_site.upload_views.Upload_View.as_view(), name="upload"),
    path("upload/complete/<str:token>/", museum_site.upload_views.upload_complete, name="upload_complete"),
    path("upload/delete/confirm/", museum_site.upload_views.Upload_Delete_Confirmation_View.as_view(), name="upload_delete_confirm"),
    path("upload/<str:action>/", museum_site.upload_views.Upload_Action_View.as_view(), name="upload_action"),

    # /user/
    path("user/login/", museum_site.user_views.login_user, name="login_user"),
    path("user/logout/", museum_site.user_views.logout_user, name="logout_user"),
    path("user/preferences/spotlight/", museum_site.user_views.preferences_spotlight, name="user_preferences_spotlight"),
    path("user/profile/<int:user_id>/<str:unused_slug>/", museum_site.user_views.user_profile, name="user_profile"),
    path("user/profile/", museum_site.user_views.user_profile, name="my_profile"),
    path("user/forgot-username/", museum_site.user_views.forgot_username, name="forgot_username"),
    path("user/forgot-password/", museum_site.user_views.forgot_password, name="forgot_password"),
    path("user/reset-password/<str:token>/", museum_site.user_views.reset_password, name="reset_password_with_token"),
    path("user/reset-password/", museum_site.user_views.reset_password, name="reset_password"),
    path("user/activate-account/<str:token>/", museum_site.user_views.activate_account, name="activate_account_with_token"),
    path("user/activate-account/", museum_site.user_views.activate_account, name="activate_account"),
    path("user/resend-activation/", museum_site.user_views.resend_account_activation, name="resend_activation"),
    path("user/change-char/", museum_site.user_views.change_char, name="change_char"),
    path("user/change-email/", museum_site.user_views.change_email, name="change_email"),
    path("user/change-password/", museum_site.user_views.change_password, name="change_password"),
    path("user/change-patron-email/", museum_site.user_views.change_patron_email, name="change_patron_email"),
    path("user/change-username/", museum_site.user_views.change_username, name="change_username"),
    path("user/change-pronouns/", museum_site.user_views.change_pronouns, name="change_pronouns"),
    path("user/update-tos/", museum_site.user_views.update_tos, name="update_tos"),
    path("user/manage-saved-data/", museum_site.user_views.manage_saved_data, name="manage_saved_data"),
    # User Patron Pages
    path("user/change-crediting-preferences/", museum_site.user_views.change_crediting_preferences, name="change_credit_preferences"),
    path("user/change-patronage-visibility/", museum_site.user_views.change_patronage_visibility, name="change_patronage_visibility"),
    path("user/change-stream-poll-nominations/", museum_site.user_views.change_patron_perks, name="change_stream_poll_nominations"),
    path("user/change-stream-selections/", museum_site.user_views.change_patron_perks, name="change_stream_selections"),
    path("user/change-closer-look-poll-nominations/", museum_site.user_views.change_patron_perks, name="change_closer_look_poll_nominations"),
    path("user/change-guest-stream-selections/", museum_site.user_views.change_patron_perks, name="change_guest_stream_selections"),
    path("user/change-closer-look-selections/", museum_site.user_views.change_patron_perks, name="change_closer_look_selections"),
    path("user/change-bkzzt-topics/", museum_site.user_views.change_patron_perks, name="change_bkzzt_topics"),

    # /*/ -- Miscellaneous Pages
    path("ascii/", museum_site.views.Ascii_Reference_View.as_view(), name="ascii"),
    path("audio-player/", museum_site.views.Audio_Player_View.as_view(), name="audio_player"),
    path("beta-unlock/", museum_site.views.beta_unlock, name="beta_unlock"),
    path("explicit-warning/", museum_site.views.explicit_warning, name="explicit_warning"),
    path("discord/", museum_site.views.Discord_Overview_View.as_view(), name="discord"),
    path("credits/", museum_site.views.site_credits, name="credits"),
    path("patron-articles/", museum_site.article_views.patron_articles, name="patron_articles"),
    path("worlds-of-zzt/", museum_site.views.worlds_of_zzt_queue, name="worlds_of_zzt"),
    path("zeta-live/", museum_site.zeta_views.zeta_live),
    # Non-Museum Websites
    path("beyond-worlds/", RedirectView.as_view(url="https://www.youtube.com/playlist?list=PL71MurckxMeAqgTNOpQ7a_EFQBsRcClWx"), name="beyond_worlds"),
    path("twitter/", RedirectView.as_view(url="https://twitter.com/worldsofzzt"), name="twitter"),
    path("tumblr/", RedirectView.as_view(url="http://worldsofzzt.tumblr.com"), name="tumblr"),
    path("patreon/", RedirectView.as_view(url="https://patreon.com/worldsofzzt"), name="patreon"),
    path("mastodon/", RedirectView.as_view(url="https://mastodon.social/@worldsofzzt"), name="mastodon"),
    path("strawpoll/", museum_site.views.strawpoll, name="strawpoll"),
    path("youtube/", RedirectView.as_view(url="https://www.youtube.com/@WorldsofZZT"), name="youtube"),
    path("twitch/", RedirectView.as_view(url="https://twitch.tv/worldsofzzt"), name="twitch"),
    path("github/", RedirectView.as_view(url="https://github.com/DrDos0016/museum-of-zzt"), name="git"),

    # Directories
    path("directory/<slug:category>/", museum_site.views.directory, name="directory"),

    # Legacy Redirects -- URLs which have changed but should still work to prevent link-rot
    path("review/<str:letter>/<str:key>/", legacy_redirect, {"name": "zfile_review", "strip": ["letter"]}),
    path("browse/", legacy_redirect, {"name": "zfile_browse"}),
    path("browse/<str:letter>/", legacy_redirect, {"name": "zfile_browse_letter"}),
    path("new/", legacy_redirect, {"name": "zfile_browse_new_releases"}),
    path("new-releases/", legacy_redirect, {"name": "zfile_browse_new_releases"}),
]

# Serve static files on DEV
if DEBUG:
    urlpatterns += static("/zgames", document_root=os.path.join(BASE_DIR, "zgames"))
