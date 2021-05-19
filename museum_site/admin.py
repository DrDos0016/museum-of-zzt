from django.contrib import admin

# Register your models here.
from .alias import Alias
from .article import Article
from .comment import Comment
from .file import File
from .detail import Detail
from .profile import Profile
from .review import Review
from .upload import Upload
from .wozzt_queue import WoZZT_Queue
from .zeta_config import Zeta_Config

admin.site.register(File)
admin.site.register(Article)
admin.site.register(Detail)
admin.site.register(Review)
admin.site.register(Upload)
admin.site.register(Alias)
admin.site.register(WoZZT_Queue)
admin.site.register(Zeta_Config)
admin.site.register(Profile)
