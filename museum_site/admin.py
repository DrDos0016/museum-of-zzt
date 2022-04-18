from django.contrib import admin

# Register your models here.
from museum_site.models.alias import Alias
from museum_site.models.article import Article
from museum_site.models.file import File
from museum_site.models.detail import Detail
from museum_site.models.download import Download
from museum_site.models.profile import Profile
from museum_site.models.review import Review
from museum_site.models.scroll import Scroll
from museum_site.models.series import Series
from museum_site.models.upload import Upload
from museum_site.models.wozzt_queue import WoZZT_Queue
from museum_site.models.zeta_config import Zeta_Config

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
