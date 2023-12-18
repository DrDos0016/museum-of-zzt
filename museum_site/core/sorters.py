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


class ZFile_Sorter(Sorter):
    sort_options = [
        {"tag": "basic", "text": "Title", "val": "title", "db_ordering": ["sort_title"]},
        {"tag": "basic", "text": "Author", "val": "author", "db_ordering": ["authors__title", "sort_title"]},
        {"tag": "basic", "text": "Company", "val": "company", "db_ordering": ["companies__title", "sort_title"]},
        {"tag": "basic", "text": "Rating", "val": "rating", "db_ordering": ["-rating", "sort_title"]},
        {"tag": "basic", "text": "Release Date (Newest)", "val": "-release", "db_ordering": ["release_date", "sort_title"]},
        {"tag": "basic", "text": "Release Date (Oldest)", "val": "release", "db_ordering": ["-release_date", "sort_title"]},
        {"tag": "publish-date", "text": "Publication Date", "val": "-publish_date", "db_ordering": ["-publish_date", "sort_title"]},
        {"tag": "upload-date", "text": "Upload Date", "val": "uploaded", "db_ordering": ["-id"]},
        {"tag": "random", "text": "Random", "val": "random", "db_ordering": ["-publish_date", "sort_title"]},
        {"tag": "debug", "text": "!ID (Newest)", "val": "-id", "db_ordering": ["-id"]},
        {"tag": "debug", "text": "!ID (Oldest)", "val": "id", "db_ordering": ["id"]},
    ]
