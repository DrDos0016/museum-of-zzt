from django.contrib import admin

# Register your models here.
from museum_site.models import *

admin.site.register(File, ZFile_Admin)
admin.site.register(Article)
admin.site.register(Author)
admin.site.register(Collection)
admin.site.register(Collection_Entry)
admin.site.register(Company)
admin.site.register(Detail)
admin.site.register(Download)
admin.site.register(Feedback_Tag)
admin.site.register(Review)
admin.site.register(Upload)
admin.site.register(Alias)
admin.site.register(WoZZT_Queue)
admin.site.register(Zeta_Config)
admin.site.register(Profile)
admin.site.register(Series)
admin.site.register(Scroll)
admin.site.register(Genre)
