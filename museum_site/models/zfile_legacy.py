import os

from museum.settings import STATIC_URL
from museum_site.core.detail_identifiers import *


class ZFile_Legacy:
    @property
    def author(self):
        """ Former DB field consisting of a slash seprated string used in Publication Pack entry headings """
        return "/".join(self.related_list("authors"))
