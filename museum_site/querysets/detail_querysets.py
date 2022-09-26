from museum_site.core.detail_identifiers import *
from museum_site.querysets.base import Base_Queryset


class Detail_Queryset(Base_Queryset):
    def visible(self):
        return self.filter(visible=True)

    def advanced_search_categories(self, include_hidden=False):
        os_details = [DETAIL_DOS, DETAIL_WIN16, DETAIL_WIN32, DETAIL_WIN64, DETAIL_OSX, DETAIL_LINUX]

        qs = self.all()
        if not include_hidden:
            qs = qs.exclude(pk=DETAIL_REMOVED)
            qs = qs.exclude(pk=DETAIL_NEW_FIND)
        cats = []

        for d in qs:
            if not d.visible:
                cats.append({"priority": 99, "header": "Hidden", "d": d})
                continue
            if d.title.startswith("ZZT "):
                cats.append({"priority": 10, "header": "ZZT", "d": d})
            elif d.title.startswith("Super ZZT "):
                cats.append({"priority": 20, "header": "Super ZZT", "d": d})
            elif (d.title in ["Image", "Video", "Audio", "Text", "ZZM Audio", "HTML Document"]):  # Media
                cats.append({"priority": 30, "header": "Media", "d": d})
            elif d.id in os_details:
                cats.append({"priority": 90, "header": "OS", "d": d})
            else:
                cats.append({"priority": 80, "header": "Other", "d": d})

        cats.sort(key=lambda k: k["priority"])
        return cats
