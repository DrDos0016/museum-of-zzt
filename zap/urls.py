import os

from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView
from django.urls import include, path

import zap.views

urlpatterns = [
    path("", zap.views.index, name="zap_index"),
    path("ajax/save-image-render/", zap.views.save_image_render, name="ajax_save_image_render"),
    #path("<slug:form_key>/", zap.views.prefab_form, name="zap_prefab"),
    path("media-upload/", zap.views.media_upload, name="zap_media_upload"),
    path("post/create/", zap.views.post_create, name="zap_create_post"),
    path("post/boost/", zap.views.post_boost, name="zap_boost_post"),
    path("post/reply/", zap.views.post_reply, name="zap_reply_post"),
    path("post/select/", zap.views.post_select, name="zap_post_select"),
    path("publication-pack/share/", zap.views.share_publication_pack, name="zap_share_publication_pack"),
    path("view/<int:pk>/", zap.views.view_event, name="zap_view_event"),
    path("preview/<slug:form_key>/", zap.views.preview, name="zap_preview"),
]
