from museum_site.querysets.base import Base_Queryset


class Genre_Queryset(Base_Queryset):
    def visible_genre_list(self):
        return self.filter(visible=True).values_list("title", flat=True)

    def visible(self):
        return self.filter(visible=True)
