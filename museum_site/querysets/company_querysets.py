from museum_site.querysets.base import Base_Queryset


class Company_Queryset(Base_Queryset):
    def company_suggestions(self):
        return self.all().only("title").distinct().order_by("title")
