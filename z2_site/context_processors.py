# coding=utf-8
from z2_site.models import Detail, File

def get_fg(request):
    print "CP GETTING FEATURED GAME"
    featured = Detail.objects.get(pk=7)
    fg = featured.file_set.all().order_by("?")[0]
    
    #fg = File.objects.get(pk=26)
    return {"fg":fg}