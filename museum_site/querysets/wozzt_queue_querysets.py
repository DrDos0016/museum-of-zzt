from museum_site.querysets.base import Base_Queryset


class WoZZT_Queue_Queryset(Base_Queryset):
    def queue_for_category(self, category):
        return self.filter(category=category).order_by("-priority", "id")
