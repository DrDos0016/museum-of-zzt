import json
import random
import requests

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .constants import (
    UPLOAD_CONTACT_NONE, UPLOAD_CONTACT_REJECTION, UPLOAD_CONTACT_ALL,
    HOST
)

from .private import NEW_UPLOAD_WEBHOOK_URL


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
    user            -- Uploader user account
    notes           -- Uploader notes
    email           -- Uploader email
    contact         -- Contact preferences
    contacted       -- Has been contacted: Y/N
    announced       -- Announced on Discord via webhook: Y/N
    """
    file = models.ForeignKey("File", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(
        default=timezone.now,
        help_text="Date upload occurred"
    )
    edit_token = models.CharField(max_length=16)
    ip = models.GenericIPAddressField(blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    email = models.EmailField(blank=True, null=True)
    contact = models.IntegerField(
        default=UPLOAD_CONTACT_NONE,
        choices=UPLOAD_CONTACT_LIST
    )
    contacted = models.BooleanField(default=False)
    announced = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        title = self.file.title if self.file else "NULL"
        output = "[{}] Upload of '{}'".format(
            self.id,
            title
        )
        return output

    def from_request(self, request, file_id, save=True):
        self.file_id = file_id
        if not self.edit_token:
            self.generate_edit_token()
        self.notes = request.POST.get("notes", "")
        self.email = request.POST.get("email")
        self.contact = int(request.POST.get("contact", 0))
        self.ip = request.META.get("REMOTE_ADDR")

        # Assign user if logged in
        if request.user.is_authenticated:
            self.user_id = request.user.id

        if save:
            self.save()

    def contact_str(self):
        return UPLOAD_CONTACT_LIST[self.contact]

    def edit_token_url(self):
        return self.edit_token

    def generate_edit_token(self, force=True):
        if self.edit_token and not force:
            return False
        self.edit_token = ""
        while len(self.edit_token) < 12:
            self.edit_token += random.choice("0123456789ABCDEF")
        self.edit_token += str(self.file_id)
        return True
