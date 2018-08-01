from museum_site.models import File
from museum_site.common import DETAIL_ZZT, DETAIL_UPLOADED, DETAIL_GFX


def displayable_files():
    return File.objects.filter(details__in=[DETAIL_ZZT]).exclude(details__in=[DETAIL_UPLOADED, DETAIL_GFX])
