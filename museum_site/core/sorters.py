class Sorter():
    """ Base Class - Not to be used directly """
    sort_options = []

    def get_sort_options_as_django_choices(self, include_tags=["basic"], exclude_tags=[], include_all=False):
        output = []
        for sort in self.sort_options:
            if include_all:
                output.append((sort["val"], sort["text"]))
                continue

            if sort.get("tag") in include_tags:
                if sort.get("tag") not in exclude_tags:
                    output.append((sort["val"], sort["text"]))
        return output

    def get_sort_options(self, include_tags=["basic"], exclude_tags=[], include_all=False):
        output = []
        for sort in self.sort_options:
            if include_all:
                output.append(sort)
                continue

            if sort.get("visible") or sort.get("tag", "") in include_tags:
                if sort.get("tag") not in exclude_tags:
                    output.append(sort)
        return output

    def get_db_ordering_for_value(self, value):
        for sort in self.sort_options:
            if sort["val"] == value:
                return sort["db_ordering"]
        return None


class Article_Sorter(Sorter):
    sort_options = [
        {"tag": "basic", "text": "Publication Date (Newest)", "val": "-date", "db_ordering": ["-publish_date", "title"]},
        {"tag": "basic", "text": "Publication Date (Oldest)", "val": "date", "db_ordering": ["publish_date", "title"]},
        {"tag": "basic", "text": "Title", "val": "title", "db_ordering": ["title"]},
        {"tag": "basic", "text": "Author", "val": "author", "db_ordering": ["author", "title"]},
        {"tag": "basic", "text": "Category", "val": "category", "db_ordering": ["category", "title"]},
    ]


class Collection_Sorter(Sorter):
    sort_options = [
        {"tag": "basic", "text": "Newest", "val": "-modified", "db_ordering": ["-modified", "title"]},
        {"tag": "basic", "text": "Oldest", "val": "modified", "db_ordering": ["modified", "title"]},
        {"tag": "basic", "text": "Title", "val": "title", "db_ordering": ["title"]},
        {"tag": "basic", "text": "Author", "val": "author", "db_ordering": ["user__username", "title"]},
        {"tag": "debug", "text": "!ID (Newest)", "val": "-id", "db_ordering": ["-id"]},
        {"tag": "debug", "text": "!ID (Oldest)", "val": "id", "db_ordering": ["id"]},
    ]


class Collection_Entry_Sorter(Sorter):
    sort_options = [
        {"tag": "basic", "text": "Collection Order", "val": "canonical", "db_ordering": ["order"]},
        {"tag": "basic", "text": "Title", "val": "title", "db_ordering": ["zfile__sort_title"]},
        {"tag": "basic", "text": "Author", "val": "author", "db_ordering": ["zfile__authors__title", "zfile__sort_title"]},
        {"tag": "basic", "text": "Company", "val": "company", "db_ordering": ["zfile__companies__title", "zfile__sort_title"]},
        {"tag": "basic", "text": "Rating", "val": "rating", "db_ordering": ["-zfile__rating", "zfile__sort_title"]},
        {"tag": "basic", "text": "Release Date (Newest)", "val": "-release", "db_ordering": ["-zfile__release_date", "zfile__sort_title"]},
        {"tag": "basic", "text": "Release Date (Oldest)", "val": "release", "db_ordering": ["zfile__release_date", "zfile__sort_title"]},
        {"tag": "debug", "text": "!ID (Newest)", "val": "-id", "db_ordering": ["-id"]},
        {"tag": "debug", "text": "!ID (Oldest)", "val": "id", "db_ordering": ["id"]},
    ]


class Feedback_Sorter(Sorter):
    sort_options = [
        {"tag": "basic", "text": "Newest", "val": "-date", "db_ordering": ["-date", "zfile__sort_title"]},
        {"tag": "basic", "text": "Oldest", "val": "date", "db_ordering": ["date", "zfile__sort_title"]},
        {"tag": "basic", "text": "File", "val": "file", "db_ordering": ["zfile__sort_title"]},
        {"tag": "basic", "text": "Feedback Author", "val": "reviewer", "db_ordering": ["author", "zfile__sort_title"]},
        {"tag": "basic", "text": "Rating", "val": "rating", "db_ordering": ["-rating", "zfile__sort_title"]},
        {"tag": "debug", "text": "!ID (Newest)", "val": "-id", "db_ordering": ["-id"]},
        {"tag": "debug", "text": "!ID (Oldest)", "val": "id", "db_ordering": ["id"]},
    ]


class Scroll_Sorter(Sorter):
    sort_options = [
        {"tag": "basic", "text": "Newest", "val": "-pk", "db_ordering": ["-pk"]},
        {"tag": "basic", "text": "Oldest", "val": "pk", "db_ordering": ["pk"]},
        {"tag": "basic", "text": "Title", "val": "title", "db_ordering": ["title"]},
        {"tag": "basic", "text": "File", "val": "file", "db_ordering": ["zfile__sort_title"]},
    ]


class Series_Sorter(Sorter):
    sort_options = [
        {"tag": "basic", "text": "Newest Entry", "val": "latest", "db_ordering": ["-last_entry_date", "title"]},
        {"tag": "basic", "text": "Title", "val": "title", "db_ordering": ["title"]},
        {"tag": "debug", "text": "!ID (Newest)", "val": "-id", "db_ordering": ["-id"]},
        {"tag": "debug", "text": "!ID (Oldest)", "val": "id", "db_ordering": ["id"]},
    ]


class ZFile_Sorter(Sorter):
    sort_options = [
        {"tag": "basic", "text": "Title", "val": "title", "db_ordering": ["sort_title"]},
        {"tag": "basic", "text": "Author", "val": "author", "db_ordering": ["authors__title", "sort_title"]},
        {"tag": "basic", "text": "Company", "val": "company", "db_ordering": ["companies__title", "sort_title"]},
        {"tag": "basic", "text": "Rating", "val": "rating", "db_ordering": ["-rating", "sort_title"]},
        {"tag": "basic", "text": "Release Date (Newest)", "val": "-release", "db_ordering": ["-release_date", "sort_title"]},
        {"tag": "basic", "text": "Release Date (Oldest)", "val": "release", "db_ordering": ["release_date", "sort_title"]},
        {"tag": "publish-date", "text": "Publication Date", "val": "-publish_date", "db_ordering": ["-publish_date", "sort_title"]},
        {"tag": "upload-date", "text": "Upload Date", "val": "uploaded", "db_ordering": ["-id"]},
        {"tag": "random", "text": "Random", "val": "random", "db_ordering": ["?"]},
        {"tag": "debug", "text": "!ID (Newest)", "val": "-id", "db_ordering": ["-id"]},
        {"tag": "debug", "text": "!ID (Oldest)", "val": "id", "db_ordering": ["id"]},
    ]
