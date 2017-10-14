from django.conf.urls import url

import poll.views

urlpatterns = [
    url(r"^$", poll.views.index, name="poll_index"),
    url(r"^results/(?P<poll_id>[0-9]+)$", poll.views.index, name="poll_index"),
]
