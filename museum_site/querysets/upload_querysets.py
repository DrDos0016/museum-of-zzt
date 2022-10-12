from museum_site.core.detail_identifiers import *
from museum_site.querysets.base import Base_Queryset


class Upload_Queryset(Base_Queryset):
    def unpublished_user_uploads(self, user_id):
        return self.filter(user_id=user_id, file__details=DETAIL_UPLOADED).order_by("-id")

    def uploads_from_tokens(self, tokens):
        """ Returns all uploads with provided tokens. This includes uploads which have been published. """
        return self.filter(edit_token__in=tokens).order_by("-id")

    def from_token(self, token):
        qs = self.filter(edit_token=token)
        if qs:
            return qs.first()
        return None
