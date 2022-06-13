import os
import zipfile

from django.db import models

from museum_site.common import (
    slash_separated_sort, zipinfo_datetime_tuple_to_str, UPLOAD_CAP,
    STATIC_PATH, optimize_image, epoch_to_unknown, record,
    redirect_with_querystring
)

from museum_site.core.detail_identifiers import *


class Content(models.Model):
    """ Representation of Files contained within a Zip File """
    model_name = "Contents"

    title = models.CharField(max_length=120, db_index=True, editable=False, help_text="Filename")
    path = models.CharField(max_length=120, db_index=True, editable=False, help_text="File Path")
    ext = models.CharField(max_length=120, db_index=True, editable=False, help_text="File Extension", blank=True)
    mod_date = models.DateTimeField(default=None, help_text="File modification datetime")
    directory = models.BooleanField(default=False)
    crc32 = models.CharField(max_length=12, editable=False, help_text="File's CRC32")
    size = models.IntegerField(editable=False, help_text="File size in bytes")

    def __str__(self):
        return self.title

    def generate_content_object(zfile, save=True):
        if not zfile.file_exists():
            return False

        try:
            zf = zipfile.ZipFile(zfile.phys_path())
        except zipfile.BadZipFile:
            return False

        # Remove old content
        content = zfile.content.all()
        for c in content:
            c.delete()

        # Add current content
        for zi in zf.infolist():
            zfile_id = zfile.id

            title = os.path.basename(zi.filename)
            path = zi.filename
            ext = os.path.splitext(zi.filename)[1]
            mod_date = zipinfo_datetime_tuple_to_str(zi)
            directory = zi.is_dir()
            crc32 = zi.CRC
            size = zi.file_size

            content = Content(
                title=title,
                path=path,
                ext=ext,
                mod_date=mod_date,
                directory=directory,
                crc32=crc32,
                size=size,
            )

            if save:
                content.save()
                zfile.content.add(content)

        return True
