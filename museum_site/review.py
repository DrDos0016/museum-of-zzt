from datetime import datetime

from django.db import models

class Review(models.Model):
    """ Review object repesenting an review to a file

    Fields:
    file            -- Link to File object
    title           -- Title of the review
    author          -- Author of the review
    email           -- Author's email (hide this? Optional?)
    content         -- Body of review
    rating          -- Rating given to file from 0.0 - 5.0
    date            -- Date review was written
    ip              -- IP address posting the review
    """
    file = models.ForeignKey("File", on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    content = models.TextField()
    rating = models.FloatField(default=5.0)
    date = models.DateField()
    ip = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        x = ("[" + str(self.id) + "] Review for " + str(self.file.title) + " [" +
             str(self.file.filename) + "] by " + str(self.author)
             )
        return x

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
