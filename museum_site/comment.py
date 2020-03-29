from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Comment():
    """ Review object repesenting a comment on an article

    Fields:
    article         -- Link to Article object
    user            -- UserID who posted comment
    content         -- Body of comment
    date            -- Date review was written
    ip              -- IP address posting the review
    """
    article = models.ForeignKey("Article", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    content = models.TextField()
    date = models.DateField()
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        output = "[{}] Comment on '{}' by {}".format(
            self.id, self.article.title, self.user
        )

        return output

    def from_request(self, request):
        if request.method != "POST":
            return False

        self.file_id = int(request.POST.get("file_id"))
        self.title = request.POST.get("title")
        self.author = request.POST.get("name")  # NAME not author
        self.email = request.POST.get("email")
        self.content = request.POST.get("content")
        self.rating = round(float(request.POST.get("rating")), 2)
        self.date = datetime.utcnow()
        self.ip = request.META["REMOTE_ADDR"]

        return True
