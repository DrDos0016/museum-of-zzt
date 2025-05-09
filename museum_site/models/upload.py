import json
import random

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from museum_site.models.base import BaseModel
from museum_site.querysets.upload_querysets import *


class Upload(BaseModel):
    """ Review object repesenting an review to a file """
    objects = Upload_Queryset.as_manager()
    model_name = "Upload"

    # Fields
    date = models.DateTimeField(default=timezone.now, help_text="Date upload occurred")
    edit_token = models.CharField(max_length=16)
    ip = models.GenericIPAddressField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    announced = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        output = "Upload #{}".format(self.pk)
        return output

    def edit_token_url(self):
        return self.edit_token

    def generate_edit_token(self, force=True):
        if self.edit_token and not force:
            return False
        self.edit_token = ""
        while len(self.edit_token) < 16:
            self.edit_token += random.choice("0123456789ABCDEF")
        return True

    def scrub(self):
        self.edit_token = ""
        self.ip = ""
        self.notes = "Blanked notes."
        self.user_id = None
