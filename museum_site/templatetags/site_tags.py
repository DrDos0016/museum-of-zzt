import os
import urllib.parse

from datetime import datetime

from django import template
from django.template import Template, Context, Library
from django.template.loader import render_to_string
from django.template.defaultfilters import stringfilter
from django.template import defaultfilters as filters
from django.utils.safestring import mark_safe

from museum.settings import STATIC_URL
from museum_site.models import File, Article
from museum_site.constants import (
    ADMIN_NAME, SITE_ROOT, TIER_NAMES, PROTOCOL, DOMAIN, LANGUAGES
)

register = Library()

LOOKUPS = {
    "language": LANGUAGES,
}


@register.filter
def as_template(raw):
    context_data = {"TODO": "TODO", "CROP": "CROP"}
    raw = "{% load static %}\n{% load site_tags %}\n{% load zzt_tags %}" + raw
    return Template(raw).render(Context(context_data))


@register.filter
def get_articles_by_id(raw):
    if "-" in raw:
        ends = raw.split("-")
        ids = list(range(int(ends[0]), int(ends[1]) + 1))
    else:
        ids = list(map(int, raw.split(",")))
    qs = Article.objects.filter(pk__in=ids)
    articles = {}
    for a in qs:
        articles[str(a.id)] = a
    return articles


@register.filter
def get_files_by_id(raw):
    ids = list(map(int, raw.split(",")))
    qs = File.objects.filter(pk__in=ids)
    files = {}
    for f in qs:
        files[str(f.id)] = f
    return files


@register.filter(name="tiername")
@stringfilter
def tiername_filter(raw):
    output = TIER_NAMES.get(raw, "Unknown Tier Or No Tier Selected")
    return output


@register.filter(name="zfill")
@stringfilter
def zfill_filter(raw, length):
    output = raw.zfill(length)
    return output


@register.filter
def url_parse(raw):
    output = urllib.parse.quote(raw)
    return output


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
                {}

            </div>
        </div>
    </div>
    """
    skip_link = kwargs.get("key", "#end-cw")

    if not kwargs.get("noskip"):
        skip_text = ' | <a href="{}">Jump past warned content</a>'.format(
            skip_link
        )
    else:
        skip_text = ""

    output = output.format(", ".join(args).title(), skip_link, skip_text)

    return mark_safe(output + "\n")


@register.simple_tag()
def guide_words(*args, **kwargs):
    sort = kwargs.get("sort", "")
    model = kwargs.get("model")
    items = (kwargs.get("first_item"), kwargs.get("last_item"))
    link_text = ["???", "???"]

    if sort is None:
        sort = ""

    output = ""
    if model == "File":
        # Figure out link text
        for x in range(0, len(link_text)):
            if sort == "author":
                if items[x].author:
                    link_text[x] = items[x].author
                else:
                    link_text[x] = "-Unknown Author-"  # This shouldn't appear
            elif sort == "company":
                if items[x].company:
                    link_text[x] = items[x].company
                else:
                    link_text[x] = "-No company-"
            elif sort == "rating":
                if items[x].rating:
                    link_text[x] = items[x].rating
                else:
                    link_text[x] = "-No Rating-"
            elif "release" in sort:
                if items[x].release_date:
                    link_text[x] = items[x].release_date.strftime("%b %d, %Y")
                else:
                    link_text[x] = "-Unknown Release Date-"
            elif "publish_date" in sort:
                if items[x].publish_date:
                    link_text[x] = items[x].publish_date.strftime("%b %d, %Y")
                else:
                    link_text[x] = "-Unknown Publication Date-"
            elif "uploaded" in sort:
                if items[x].upload_set.first().date:
                    link_text[x] = items[x].upload_set.first().date.strftime(
                        "%b %d, %Y"
                    )
                else:
                    link_text[x] = "-Unknown Upload Date-"
            elif "id" in sort:
                link_text[x] = "[{}] {}".format(items[x].id, items[x].title)
            else:  # Title
                link_text[x] = items[x].title

        if items[0] != "" and items[1] != "":
            output = """
            <div class="guide-words">
                <span><a class="left" href="#{}">{}</a></span>
                <span><a class="right" href="#{}">{}</a></span>
            </div>
            """.format(
                items[0].filename, link_text[0],
                items[1].filename, link_text[1]
            )
        else:
            output = ""
    elif model == "Article":
        # Figure out link text
        for x in range(0, len(link_text)):
            if sort == "author":
                if items[x].author:
                    link_text[x] = items[x].author
                else:
                    link_text[x] = "-Unknown Author-"  # This shouldn't appear
            elif sort == "-date" or sort == "date":
                if items[x].publish_date and items[x].publish_date.year > 1970:
                    link_text[x] = items[x].publish_date.strftime("%b %d, %Y")
                else:
                    link_text[x] = "-Unknown Date-"
            elif sort == "category":
                link_text[x] = items[x].category
            elif "id" in sort:
                link_text[x] = "[{}] {}".format(items[x].id, items[x].title)
            else:  # Title
                link_text[x] = items[x].title

        if items[0] != "" and items[1] != "":
            output = """
            <div class="guide-words">
                <span><a class="left" href="#article-{}">{}</a></span>
                <span><a class="right" href="#article-{}">{}</a></span>
            </div>
            """.format(
                items[0].id, link_text[0],
                items[1].id, link_text[1]
            )
        else:
            output = ""

    return mark_safe(output + "\n")


@register.simple_tag()
def meta_tags(*args, **kwargs):
    # url = kwargs.get("url", "https://museumofzzt.com/").split("?")[0]

    # Default values
    base_url = "{}://{}".format(PROTOCOL, DOMAIN)
    path = kwargs.get("path", "").split("?")[0]  # Sans QS
    url = base_url + path
    og_default = "{}{}images/og_default.jpg".format(base_url, STATIC_URL)
    tags = {
        "author": ["name", ADMIN_NAME],
        "description": [
            "name",
            "The Museum of ZZT is an online archive dedicated to the "
            "preservation and curation of ZZT worlds. Explore more than 3000 "
            "indie-made ZZT worlds spanning its 30+ year history"
        ],
        "og:type": ["property", "website"],
        "og:url": ["property", url],
        "og:title": ["property", "Museum of ZZT"],
        "og:image": ["property", og_default],
    }

    if kwargs.get("article"):
        tags["author"][1] = kwargs["article"].author
        tags["description"][1] = kwargs["article"].description
        tags["og:title"][1] = kwargs["article"].title + " - Museum of ZZT"
        tags["og:image"][1] = base_url + kwargs["article"].preview
    elif kwargs.get("file") and kwargs.get("file") != "Local File Viewer":
        tags["author"][1] = kwargs["file"].author
        tags["description"][1] = '{} by {}'.format(
            kwargs["file"].title, kwargs["file"].author
        )
        if kwargs["file"].company and kwargs["file"].company != "None":
            tags["description"][1] += " of {}".format(kwargs["file"].company)
        if kwargs["file"].release_date:
            tags["description"][1] += " ({})".format(
                kwargs["file"].release_date.year
            )
        tags["og:title"][1] = kwargs["file"].title + " - Museum of ZZT"
        tags["og:image"][1] = base_url + STATIC_URL + (
            kwargs["file"].screenshot_url()
        )

    # Overrides
    if kwargs.get("author"):
        tags["author"][1] = kwargs["author"]
    if kwargs.get("description"):
        tags["description"][1] = kwargs["description"]
    if kwargs.get("title"):
        tags["og:title"][1] = kwargs["title"] + " - Museum of ZZT"
    if kwargs.get("og_image"):
        tags["og:image"][1] = "https://museumofzzt.com/" + STATIC_URL[1:] + (
            kwargs["og_image"]
        )

    # Twitter tags
    tags["twitter:site"] = ["name", "@worldsofzzt"]
    tags["twitter:card"] = ["name", "summary_large_image"]
    tags["twitter:title"] = ["name", tags["og:title"][1]]
    tags["twitter:description"] = ["name", tags["description"][1]]
    tags["twitter:image"] = ["name", tags["og:image"][1]]

    # Assemble HTML meta tags
    BLANK = '<meta {}="{}" content="{}">\n'
    meta_tag_html = ""
    for key in tags.keys():
        meta_tag_html += BLANK.format(tags[key][0], key, tags[key][1])

    return mark_safe(meta_tag_html[:-1])


@register.simple_tag()
def patreon_plug(*args, **kwargs):
    output = """
        <div class="patreon-plug">
        <div class="text">
            <div class="heading">
            <span>======</span> A Worlds of ZZT Production <span>======</span>
            </div>
            <p>
               The Worlds of ZZT project is
               committed to the preservation
               of ZZT and its history.</p>

               <p> This article was produced
               thanks to supporters on Patreon.</p>

            <a href="https://patreon.com/worldsofzzt" target="_blank">
            Support Worlds of ZZT on Patreon!</a>
        </div>
    </div>
    """

    return mark_safe(output + "\n")


@register.simple_tag()
def cl_info(pk=None, engine=None, emulator=None):
    if pk is None:
        zfile = File()
        zfile.id = -1
    else:
        zfile = File.objects.get(pk=pk)

    if zfile.company:
        company = "Published Under: {}<br>".format(zfile.company)
    else:
        company = ""

    if zfile.release_date is not None:
        release = zfile.release_date.strftime("%B %m, %Y")
    else:
        release = "Unknown"

    output = """
        <div class="c">
            <h2>{title}</h2>
            By: {author}<br>
            {company}
            Released: {release}
    """.format(
        title=zfile.title, author=zfile.author, company=company, release=release
    )

    if engine:
        output += "<br>Played Using: " + engine
    if emulator:
        output += " via " + emulator

    output += (
        '<br><a href="{download}" target="_blank">Download</a> | '
        '<a href="{play}" target="_blank">Play Online</a> | '
        '<a href="{view}" target="_blank">View Files</a><br>'
    ).format(
        download=zfile.download_url(),
        play=zfile.play_url(),
        view=zfile.file_url()
    )

    output += "<br>\t</div>"

    return mark_safe(output + "\n")


@register.tag(name="commentary")
def commentary(parser, token):
    nodelist = parser.parse(('endcommentary',))
    parser.delete_first_token()
    return Commentary(nodelist)


class Commentary(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        nodes = self.nodelist
        material = ""
        commentary = ""

        idx = 0
        for n in nodes[:-1]:
            rendered = n.render(context)

            # Manually break on a split
            if "<!--Split-->" in rendered:
                break

            material += rendered
            idx += 1

        # All remaining nodes are for commentary
        commentary_nodes = nodes[idx:]

        for c in commentary_nodes:
            rendered = c.render(context).replace("<!--Split-->", "")
            commentary += rendered

        commentary = commentary.strip()
        if (commentary and commentary[0] != "<") or commentary.startswith("<!"):
            commentary = (
                "<p>" + commentary.replace("\r\n\r\n", "</p><p>").replace(
                    "\n\n", "</p><p>"
                ) + "</p>"
            )

        debug_classes = ""
        if "TODO" in commentary:
            debug_classes += " TODO"
        if "CROP" in commentary:
            debug_classes += "CROP"

        output = """
<div class="side-commentary{debug_classes}">
    <div class="material">
    {material}
    </div>
    <div class="commentary">
        {commentary}
    </div>
</div>
"""
        return output.format(
            debug_classes=debug_classes,
            material=material,
            commentary=commentary
        )


@register.tag(name="il")
def il(parser, token):
    nodelist = parser.parse(('endil',))
    parser.delete_first_token()
    # Strip the leading "il " before splitting args
    raw_args = token.contents[3:] if len(token.contents.split()) >= 2 else ""
    return IL(nodelist, raw_args)


class IL(template.Node):
    def __init__(self, nodelist, raw_args=""):
        self.args = raw_args.split("|") + ["", "", "", ""]
        self.nodelist = nodelist

    def render(self, context):
        text = self.nodelist[0].render(context)
        q = text if self.args[0] == "" else self.args[0]
        filename = "&file=" + self.args[1] if self.args[1] != "" else ""
        board = "&board=" + self.args[2] if self.args[2] != "" else ""
        coords = "#" + self.args[3] if self.args[3] != "" else ""
        url = "/search?q={}&auto=1".format(q) + filename + board + coords
        output = "<a class='il' target='_blank' href='{url}'>{text}</a>".format(
            url=url, text=text
        )
        return output


@register.tag(name="spoiler")
def spoiler(parser, token):
    nodelist = parser.parse(('endspoiler',))
    parser.delete_first_token()
    args = token.split_contents()
    display = "inline-block"
    if len(args) > 1:
        display = token.split_contents()[1]
    return Spoiler(nodelist, display)


class Spoiler(template.Node):
    def __init__(self, nodelist, display):
        self.nodelist = nodelist
        self.display = display

    def render(self, context):
        text = self.nodelist[0].render(context)
        output = "<div class='spoiler' style='display:{}'>{}</div>".format(
            self.display, text
        )
        return output


@register.simple_tag()
def ssv_links(raw, param, lookup=""):
    output = ""
    items = raw.split("/")
    lookup = LOOKUPS.get(lookup, {})

    for i in items:
        output += "<a href='/search?{}={}'>{}</a>, ".format(
            param, i, lookup.get(i, i)
        )

    return mark_safe(output[:-2] + "\n")


@register.simple_tag()
def gblock(item, view="detailed", header=None, debug=False, extras=None):
    template = "museum_site/blocks/generic-{}-block.html".format(view)
    if view =="detailed":
        context = item.detailed_block_context(extras=extras, debug=debug)
    elif view =="list":
        context = item.list_block_context(extras=extras, debug=debug)
    elif view == "gallery":
        context = item.gallery_block_context(extras=extras, debug=debug)
    output = render_to_string(template, context)
    return mark_safe(output + "\n")


@register.simple_tag()
def generic_block_loop(
    items, view="detailed", header=None, debug=False, extras=None
):
    template = "museum_site/blocks/generic-{}-block.html".format(view)
    output = ""

    # Empty sets
    if len(items) == 0:
        output = "<div id='no-results'><img src='/static/chrome/blank-board.png' %}'><p>Your query returned zero results!</p></div>"
        return mark_safe(output)

    if view == "list":
        output += "<table>{}".format(header)
    elif view == "gallery":
        output += '<div class="gallery-frame">'

    for i in items:
        if view == "detailed":
            context = i.detailed_block_context(extras=extras, debug=debug)
        elif view == "list":
            context = i.list_block_context(extras=extras, debug=debug)
        elif view == "gallery":
            context = i.gallery_block_context(extras=extras, debug=debug)
        output += render_to_string(template, context)

    if view == "list":
        output += "</table>"
    elif view == "gallery":
        output += "</div>"

    return mark_safe(output + "\n")
