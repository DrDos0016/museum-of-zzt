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
    #summary     = models.CharField(max_length=300)  # Summary of article
    content     = models.TextField()                #
    css         = models.TextField()                # Additional styling for the article
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
    letter      = models.CharField(max_length=1, db_index=True)    # #/A-Z to show up under when browsed
    description = models.TextField(null=True, default=None) # Description for Utilites
    details     = models.CharField(max_length=80, default="MS-DOS")
    review_count= models.IntegerField(default=0)    # Number of reviews on this file
    
    def download_url(self):
        return "/zgames/" + self.letter + "/" + self.filename
        
    def review_url(self):
        return "/review/" + self.letter + "/" + self.filename
        
    def file_url(self):
        return "/file/" + self.letter + "/" + self.filename
        
    def wiki_url(self):
        return "http://zzt.org/zu/wiki/" + self.title
    
"""
class Detail(models.Model):
    OS_LIST = ("MS-DOS", "Windows 16-bit", "Windows 32-bit", "Windows 64-bit", "Linux", "OSX")
    
    file        = models.OneToOneField("File", primary_key=True)        # TeamID
    os          = models.CharField(max_length=50)
"""
    
class Review(models.Model):
    file        = models.ForeignKey("File")         # Review file
    title       = models.CharField(max_length=50)   # Review title
    author      = models.CharField(max_length=50)   # Review author
    email       = models.EmailField()               # Contact info for author (hide this? Optional?)
    content     = models.TextField()                # Review content
    rating      = models.FloatField(default=5.0)    # Review Rating
    date        = models.DateField()                # Review Date
    ip          = models.IPAddressField()           # Review IP
    
    def __unicode__(self):
        x = "Review for " + self.file.title + "[" + self.file.filename + "]\n"
        x+= self.title + "\n"
        x+= self.author + "\n"
        x+= self.email + "\n"
        x+= self.content[:50] + "..." + "\n"
        x+= str(self.rating) + "\n"  
        x+= str(self.date) + "\n"
        x+= self.ip + "\n"
        return x