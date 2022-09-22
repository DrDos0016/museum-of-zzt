from museum_site.querysets.base import Base_Queryset


class Profile_Queryset(Base_Queryset):
    def patrons(self):
        return self.filter(patron=True).order_by("user__username")
