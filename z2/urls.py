from django.conf.urls import patterns, include, url
from django.views.static import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'z2_site.views.index'),
    
    # Articles
    url(r'^article$', 'z2_site.views.article_directory'),
    url(r'^article/(?P<id>[0-9]+)/(.*)$', 'z2_site.views.article_view'),
    
    # Files
    url(r'^browse/(?P<letter>[a-z1])$', 'z2_site.views.browse'),
    url(r'^file/(?P<letter>[a-z1])/(?P<filename>.*)$', 'z2_site.views.file'),
    
    # Reviews
    url(r'^review/(?P<letter>[a-z1])/(?P<filename>.*)$', 'z2_site.views.review'),
    
    # AJAX
    url(r'^ajax/get_zip_file$', 'z2_site.ajax.get_zip_file'),
    
    (r'^assets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    (r'^zgames/(?P<path>.*)$', 'django.views.static.serve', {'document_root': "/var/projects/z2/zgames/"})
)
