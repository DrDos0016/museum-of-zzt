from django.db import models
from django.db.models import Q

from museum_site.querysets.base import Base_Queryset
from museum_site.models import *

class Collection_Queryset(Base_Queryset):
    def stub(self):
        return self.all()


class Collection_Entry_Queryset(Base_Queryset):
    def duplicate_check(self, collection_id, zfile_id):
        exists = self.filter(collection_id=int(collection_id), zfile_id=int(zfile_id)).exists()
        return exists

    def get_items_in_collection(self, collection_id):
        print("GETTING", collection_id)
        qs = self.filter(collection_id=collection_id)
        return qs
