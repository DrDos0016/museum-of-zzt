from django.db import models
from django.db.models import Q

from museum_site.querysets.base import Base_Queryset
from museum_site.models import *

class Genre_Queryset(Base_Queryset):
    def visible_genre_list(self):
        return self.filter(visible=True).values_list("title", flat=True)
