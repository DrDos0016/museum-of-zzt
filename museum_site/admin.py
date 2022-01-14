from django.contrib import admin

# Register your models here.
from .alias import Alias
from .article import Article
from .file import File
from .detail import Detail
from .download import Download
from .profile import Profile
from .review import Review
from .scroll import Scroll
from .series import Series
from .upload import Upload
from .wozzt_queue import WoZZT_Queue
from .zeta_config import Zeta_Config

admin.site.register(File)
admin.site.register(Article)
admin.site.register(Detail)
admin.site.register(Download)
admin.site.register(Review)
admin.site.register(Upload)
admin.site.register(Alias)
admin.site.register(WoZZT_Queue)
admin.site.register(Zeta_Config)
admin.site.register(Profile)
admin.site.register(Series)
admin.site.register(Scroll)
