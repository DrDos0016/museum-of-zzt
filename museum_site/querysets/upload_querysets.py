from museum_site.core.detail_identifiers import *
from museum_site.querysets.base import Base_Queryset


class Upload_Queryset(Base_Queryset):
    def from_token(self, token):
        """ Get an upload object from the provided token """
        qs = self.filter(edit_token=token)
        if qs:
            return qs.first()
        return None
