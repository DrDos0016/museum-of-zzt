from museum_site.querysets.base import Base_Queryset


class Author_Queryset(Base_Queryset):
    def author_suggestions(self):
        return self.all().only("title").distinct().order_by("title")
