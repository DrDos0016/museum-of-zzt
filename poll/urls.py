from django.urls import path

import poll.views

urlpatterns = [
    path("", poll.views.index, name="poll_index"),
    path("results/<int:poll_id>/", poll.views.index, name="poll_results"),
]
