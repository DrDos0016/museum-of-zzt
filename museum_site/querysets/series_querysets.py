from museum_site.core.detail_identifiers import *
from museum_site.querysets.base import Base_Queryset


class Series_Queryset(Base_Queryset):
    def visible(self):
        return self.filter(visible=True)

    def directory(self):
        """ TODO: Replace calls to this with calls to visible() """
        return self.filter(visible=True)

    def visible_incomplete_priority(self):
        # Returns all visible series, with incomplete series coming before completed ones
        return self.filter(visible=True).order_by("complete", "title")
