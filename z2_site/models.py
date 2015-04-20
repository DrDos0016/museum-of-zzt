from django.db import models

"""
class Example(models.Model):
    chars       = models.CharField(max_length=20)
    ints        = models.IntegerField(default=0)
    ip          = models.IPAddressField(default="")
    timestamp   = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "An example."
"""

class Article(models.Model):
    title       = models.CharField(max_length=50)
    author      = models.CharField(max_length=50)
    category    = models.CharField(max_length=50)   #
    content     = models.TextField()                #
    date        = models.DateField()                #
    published   = models.BooleanField(default=False)
    file        = models.ForeignKey("File", null=True)  # Associate this article with a specific file
    
class File(models.Model):
    DETAIL_LIST = ("MS-DOS", "Windows", "Linux", "OSX", "Featured", "GOTM", "CGOTM", "MTP", "Contest", "Soundtrack", "Font", "Hack")
    
    title       = models.CharField(max_length=80)   # Frost 1: Power
    author      = models.CharField(max_length=80)   # Zenith Nadir
    filename    = models.CharField(max_length=50)   # Respite.zip
    size        = models.IntegerField(default=0)    # Filesize in Kilobytes
    genre       = models.CharField(max_length=50)   # Action, Adventure, Puzzle, Etc.
    category    = models.CharField(max_length=10)   # ZZT, Super ZZT, ZIG, Utility, Editor, Etc.
    screenshot  = models.CharField(max_length=80)   # Screenshot of title screen
    description = models.TextField(null=True, default=None) # Description for Utilites
    details     = models.CharField(max_length=80, default="MS-DOS")
    review_count= models.IntegerField(default=0)    # Number of reviews on this file
    reviews     = models.ForeignKey("Review", null=True)    # Reviews
    
class Review(models.Model):
    title       = models.CharField(max_length=50)   # Review title
    author      = models.CharField(max_length=50)   # Review author
    email       = models.EmailField()               # Contact info for author (hide this? Optional?)
    content     = models.TextField()
    rating      = models.FloatField(default=5.0)
    date        = models.DateField()
    ip          = models.IPAddressField()