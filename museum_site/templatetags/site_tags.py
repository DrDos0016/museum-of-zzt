from datetime import datetime

from django.template import Template, Context, Library
from django.utils.safestring import mark_safe

from museum_site.models import File

register = Library()


@register.filter
def as_template(raw):
    raw = "{% load staticfiles %}\n{% load site_tags %}\n{% load zzt_tags %}" + raw
    return Template(raw).render(Context())


@register.simple_tag()
def content_warning(*args, **kwargs):
    output = """
        <div class="content-warning">
        <div class="text">
            <b class="heading">CONTENT WARNING</b>
            <p>The following content contains material which may be offensive
            to some audiences. It was most likely originally created by a
            teenager who has since grown up. This material does not necessarily
            reflect its creator's current opinions nor behaviors.</p>

            <p>Specifically, this page contains depictions of or references to:
            <br><b>{}</b></p>

            <div class="controls r">
                <span class="jsLink" name="cw-hide-all">Hide all future content
                warnings</span> |
                <span class="jsLink" name="cw-hide-this"
                data-content-warning-key="{}">Hide this</span>

            </div>
        </div>
    </div>
    """
    content_warning_key = kwargs.get("key", "")

    output = output.format(", ".join(args).title(), content_warning_key)

    return mark_safe(output + "\n")


@register.simple_tag()
def patreon_plug(*args, **kwargs):
    output = """
        <div class="patreon-plug">
        <div class="text">
            <div class="heading"><span>======</span> A Worlds of ZZT Production <span>======</span></div>
            <p>
               The Worlds of ZZT project is
               committed to the preservation
               of ZZT and its history.</p>

               <p> This article was produced
               thanks to supporters on Patreon.</p>

            <a href="https://patreon.com/worldsofzzt" target="_blank">Support Worlds of ZZT on
            Patreon!</a>
        </div>
    </div>
    """

    return mark_safe(output + "\n")

@register.simple_tag()
def cl_info(id):
    file = File.objects.get(pk=id)

    if file.company:
        company = "Published Under: {}<br>".format(file.company)
    else:
        company = ""

    if file.release_date is not None:
        release = file.release_date.strftime("%B %m, %Y")
    else:
        release = "Unknown"


    output = """
        <div class="c">
            <h2>{title}</h2>
            By: {author}<br>
            {company}
            Released: {release}<br>
            <a href="{download}" target="_blank">Download</a> | <a href="{play}" target="_blank">Play Online</a> | <a href="{view}" target="_blank">View Files</a><br>
        </div>

    """.format(title=file.title, author=file.author, company=company, release=release, download=file.download_url(), play=file.play_url(), view=file.file_url())

    return mark_safe(output + "\n")

