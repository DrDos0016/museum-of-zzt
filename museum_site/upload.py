import random

from datetime import datetime

from django.db import models

from .constants import (
    UPLOAD_CONTACT_NONE, UPLOAD_CONTACT_REJECTION, UPLOAD_CONTACT_ALL
)


UPLOAD_CONTACT_LIST = (
    (UPLOAD_CONTACT_NONE, "No contact"),
    (UPLOAD_CONTACT_REJECTION, "Contact if rejected"),
    (UPLOAD_CONTACT_ALL, "Contact if published/rejected"),
)


class Upload(models.Model):
    """ Review object repesenting an review to a file

    Fields:
    file            -- Link to File object
    date            -- Date of upload
    edit_token      -- Token to modify upload
    ip              -- Uploader IP
    notes           -- Uploader notes
    email           -- Uploader email
    contact         -- Contact preferences
    contacted       -- Has been contacted: Y/N
    """
    file = models.ForeignKey("File", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date upload occurred"
    )
    edit_token = models.CharField(max_length=16)
    ip = models.GenericIPAddressField(blank=True, null=True)
    notes = models.TextField(blank=True)
    email = models.EmailField(blank=True, null=True)
    contact = models.IntegerField(
        default=UPLOAD_CONTACT_NONE,
        choices=UPLOAD_CONTACT_LIST
    )
    contacted = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        output = "[{}] Upload of '{}'".format(
            self.id,
            self.file.title
        )
        return output

    def from_request(self, request, file_id, save=True):
        self.file_id = file_id
        if not self.edit_token:
            self.edit_token = ""
            while len(self.edit_token) < 16:
                self.edit_token += random.choice("0123456789ABCDEF")
        self.notes = request.POST.get("notes", "")
        self.email = request.POST.get("email")
        self.contact = int(request.POST.get("contact", 0))
        self.ip = request.META.get("REMOTE_ADDR")

        if save:
            self.save()

    def contact_str(self):
        return UPLOAD_CONTACT_LIST[self.contact]

    def edit_token_url(self):
        return self.edit_token
