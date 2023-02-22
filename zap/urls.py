import os

from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView
from django.urls import include, path

import zap.views

urlpatterns = [
    path("", zap.views.index, name="zap_index"),
    path("<slug:form_key>/", zap.views.prefab_form, name="zap_stream_schedule"),
    path("preview/<slug:form_key>/", zap.views.preview, name="zap_preview"),
]
