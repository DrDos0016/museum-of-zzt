import json
import random
import requests

from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from museum_site.models.base import BaseModel
from museum_site.constants import HOST

from museum_site.private import NEW_UPLOAD_WEBHOOK_URL


class Upload(BaseModel):
    """ Review object repesenting an review to a file """
    model_name = "Upload"

    """
    Fields:
    file            -- Link to File object
    date            -- Date of upload
    edit_token      -- Token to modify upload
    ip              -- Uploader IP
    user            -- Uploader user account
    notes           -- Uploader notes
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

    def scrub(self):
        self.edit_token = ""
        self.ip = ""
        self.notes = "Blanked notes."
        self.contacted = False
        self.user_id = None
