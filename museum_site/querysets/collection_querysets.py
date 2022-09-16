from django.db import models
from django.db.models import Q

from museum_site.querysets.base import Base_Queryset


class Collection_Queryset(Base_Queryset):
    def duplicate_check(self, slug):
        return self.filter(slug=slug).exists()

    def check_slug_overlap(self, pk, slug):
        """ When editing a collection, make sure the requested slug isn't in use by anything other than the current collection """
        return self.exclude(pk=pk).filter(slug=slug).exists()

    def collections_for_user(self, user_id):
        return self.filter(user_id=user_id)

    def populated_public_collections(self):
        return self.filter(visibility=self.model.PUBLIC, item_count__gte=1)


class Collection_Entry_Queryset(Base_Queryset):
    def duplicate_check(self, collection_id, zfile_id):
        return self.filter(collection_id=int(collection_id), zfile_id=int(zfile_id)).exists()

    def get_items_in_collection(self, collection_id):
        qs = self.filter(collection_id=collection_id)
        return qs

    def get_latest_addition_to_collection(self, collection_id):
        return self.filter(collection_id=collection_id).order_by("-id").first()
