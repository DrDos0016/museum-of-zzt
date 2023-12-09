from django.db.models.signals import post_save
from django.dispatch import receiver

from museum_site.models import Article, File


@receiver(post_save, sender=Article)
def article_post_save(sender, instance, **kwargs):
    # Associate ZFiles with publication packs
    if instance.category == "Publication Pack":
        zfile_ids = []
        for line in instance.content.split("\n"):
            if "|get_files_by_id" in line:
                ids = line[line.find('"') + 1:]
                ids = ids[:ids.find('"')]
                zfile_ids = ids.split(",")
                break
        for i in zfile_ids:
            zf = File.objects.filter(pk=int(i)).first()
            if zf:
                zf.articles.add(instance.pk)
                zf.save()  # FULLSAVE

    # Update dates for Series
    if instance.series is not None:
        all_series = instance.series.all()
        if all_series:
            for s in all_series:
                s.save()
