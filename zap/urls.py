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
    path("create/post/", zap.views.create_post, name="zap_create_post"),
    path("create/stream-schedule/", zap.views.create_stream_schedule, name="zap_create_stream_schedule"),
    path("view/<int:pk>/", zap.views.view_event, name="zap_view_event"),
    path("preview/<slug:form_key>/", zap.views.preview, name="zap_preview"),
]
