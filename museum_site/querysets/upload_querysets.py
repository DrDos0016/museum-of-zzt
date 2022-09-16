from django.db import models
from django.db.models import Q

from museum_site.core.detail_identifiers import *
from museum_site.querysets.base import Base_Queryset
from museum_site.models import *

class Upload_Queryset(Base_Queryset):
    def unpublished_user_uploads(self, user_id):
        return self.filter(user_id=user_id, file__details=DETAIL_UPLOADED).order_by("-id")

    def from_token(self, token):
        qs = self.filter(edit_token=token)
        if qs:
            return qs.first()
        return None
