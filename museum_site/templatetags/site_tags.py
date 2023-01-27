import pprint

import urllib.parse

from django import template
from django.template import Template, Context, Library
from django.template.loader import render_to_string
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from museum.settings import STATIC_URL
from museum_site.models import File, Article
from museum_site.constants import (
    ADMIN_NAME, PROTOCOL, DOMAIN, LANGUAGES
)

register = Library()

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
    for _id in ids:
        if not files.get(str(_id)):
            files[str(_id)] = File(
                id=-1, title="ERROR: File #{} not found".format(_id),
                screenshot="red-x-error.png",
            )
    return files

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

            <div class="r">
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
    items = (kwargs.get("first_item", ""), kwargs.get("last_item", ""))
    location = kwargs.get("location", "top")
    link_text = ["???", "???"]

    if items == ("", ""):
        # Try a manually passed object list
        if kwargs.get("object_list"):
            first = kwargs["object_list"][0]
            last = kwargs["object_list"][len(kwargs["object_list"]) - 1]
            items = (first, last)

    if sort is None:
        sort = ""

    output = ""

    # Treat Collection Entries as their associated Files
    if model == "Collection Entry":
        model = "File"
        if items[0] and items[1]:
            items = (items[0].zfile, items[1].zfile)

    if model == "File":
        # Figure out link text
        for x in range(0, len(link_text)):
            if items[x] == "":
                continue
            if sort == "author":
                if items[x].authors.count():
                    link_text[x] = ", ".join(items[x].related_list("authors"))
                else:
                    link_text[x] = "-Unknown Author-"  # This shouldn't appear
            elif sort == "company":
                if items[x].companies.count():
                    link_text[x] = items[x].get_all_company_names()
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
            <div class="guide-words {}">
                <div class="l"><a class="left" href="#{}">{}</a></div>
                <div class="r"><a class="right" href="#{}">{}</a></div>
            </div>
            """.format(
                location,
                items[0].key, link_text[0],
                items[1].key, link_text[1]
            )
        else:
            output = ""
    elif model == "Article":
        # Figure out link text
        for x in range(0, len(link_text)):
            if items[x] == "":
                continue
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
                <span><a class="left" href="#{}">{}</a></span>
                <span><a class="right" href="#{}">{}</a></span>
            </div>
            """.format(
                items[0].id, link_text[0],
                items[1].id, link_text[1]
            )
        else:
            output = ""
    elif model == "Review":
        for x in range(0, len(link_text)):
            if items[x] == "":
                continue
            if sort == "file":
                link_text[x] = items[x].zfile.title
            elif sort == "reviewer":
                link_text[x] = items[x].author
            elif sort == "date" or sort == "-date":
                link_text[x] = items[x].date.strftime("%b %d, %Y")
            elif sort == "rating":
                link_text[x] = items[x].rating if items[x].rating >= 0 else "-No Rating-"

        if items[0] != "" and items[1] != "":
            output = """
            <div class="guide-words">
                <span><a class="left" href="#{}">{}</a></span>
                <span><a class="right" href="#{}">{}</a></span>
            </div>
            """.format(
                items[0].id, link_text[0],
                items[1].id, link_text[1]
            )
        else:
            output = ""
    elif model == "Collection":
        for x in range(0, len(link_text)):
            if items[x] == "":
                continue
            if sort == "modified" or sort == "-modified":
                link_text[x] = items[x].modified.strftime("%b %d, %Y")
            elif sort == "title":
                link_text[x] = items[x].title
            elif sort == "author":
                link_text[x] = items[x].user.username
            elif sort == "id" or sort == "-id":
                link_text[x] = items[x].pk

        if items[0] != "" and items[1] != "":
            output = """
            <div class="guide-words">
                <span><a class="left" href="#{}">{}</a></span>
                <span><a class="right" href="#{}">{}</a></span>
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
    # Default values
    base_url = "{}://{}{}".format(PROTOCOL, DOMAIN, STATIC_URL[:-1])
    path = kwargs.get("path", "").split("?")[0]  # Sans QS
    url = base_url + path
    og_default = "pages/og_default.jpg"
    tags = {
        "author": ["name", ADMIN_NAME],
        "description": [
            "name",
            "The Museum of ZZT is an online archive dedicated to the "
            "preservation and curation of ZZT worlds. Explore more than 3000 "
            "indie-made ZZT worlds spanning its 30+ year history"
        ],
        "og:type": ["property", "website"],
        "og:url": ["property", "{}://{}".format(PROTOCOL, DOMAIN) + path],
        "og:title": ["property", "Museum of ZZT"],
        "og:image": ["property", og_default],
    }

    if kwargs.get("context"):
        tags.update(kwargs["context"])

    # Prepend static url to image
    tags["og:image"][1] = "{}://{}".format(PROTOCOL, DOMAIN) + STATIC_URL + tags["og:image"][1]

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
        meta_tag_html += BLANK.format(
            tags[key][0], key, tags[key][1].replace('"', "'")
        )

    return mark_safe(meta_tag_html[:-1])


@register.simple_tag()
def patreon_plug(*args, **kwargs):
    return render_to_string("museum_site/subtemplate/patreon-plug.html", {})


@register.simple_tag()
def plug(service='UNKNOWN-SERVICE'):
    services = {"youtube": "YouTube"}  # Stylized spellings
    title = services.get(service, service.title())
    ext = "png" if service != "mastodon" else "svg"
    output = """
    <div class="plug plug-{0}"><a href="/{0}/" target="_blank" class="noext noul">
        <div class="logo"><img src="/static/icons/plug-{0}.{ext}"></div>
        <div class="text">Worlds of ZZT on {title}</div>
    </a></div>
    """.format(service, title=title, ext=ext)
    return mark_safe(output + "\n")


@register.simple_tag()
def zfl(key, text="", qs="", target="_blank", i=True, *args, **kwargs):
    """ ZFile Link """
    """ {% zfl codered Code Red %}"""

    key_str = key
    attrs_str = ""
    qs_str = ""
    target_str = ' target="{}"'.format(target) if target else ""

    if key.startswith("http"):
        key_str = key.split("/")[-2]
    if "?" in key:
        qs_str = "?" + key.split("?")[1]

    if text == "":
        text = "<span class='debug'>TODO: Incomplete ZFL - {}</span>".format(key_str)  # Expected TODO usage.

    if qs:
        # Convert copied/pasted URLs to just the querystring
        if qs.startswith("http"):
            qs = qs.split("?")[1]
        qs_str = "?{}".format(qs)

        # Prevent double questionmarks
        if qs_str.startswith("??"):
            qs_str = qs_str[1:]

    output = '<a href="/file/view/{}/{}"{}{}>{}</a>'.format(key_str, qs_str, target_str, attrs_str, text)

    # Italicize text if needed
    output = "<i>" + output + "</i>" if i else output
    return mark_safe(output)


@register.simple_tag(takes_context=True)
def cl_info(context, pk=None, engine=None, emulator=None):
    zfile = File.objects.filter(pk=pk).first()
    if zfile is None:
        zfile = File()
        zfile.id = -1
        zfile.title = "UNKNOWN ZFILE TODO"
        links = []
    else:
        return model_block(context, zfile, "cl_info", engine=engine, emulator=emulator)


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
        if "TODO" in commentary:  # Expected TODO usage.
            debug_classes += " TODO"  # Expected TODO usage.
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


@register.simple_tag()
def fn(num=1):
    if num > 0:
        output = "<sup><a href='#fn-{}' id='fnl-{}'>[{}]</a></sup>"
    else:
        num = -1 * num
        output = "<sup><a href='#fnl-{}' id='fn-{}'>[{}]</a></sup>"
    return mark_safe(output.format(num, num, num))


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
        output = "<a class='il' target='_blank' href='{url}'>{text}</a>".format(url=url, text=text)
        return output


@register.tag(name="notice")
def notice(parser, token):
    nodelist = parser.parse(('endnotice',))
    parser.delete_first_token()
    args = token.split_contents()
    heading = " ".join(args[1:])
    if heading[0] != '"' or heading[-1] != '"':
        heading = '"{}"'.format(heading)
    return Notice(nodelist, heading)


class Notice(template.Node):
    def __init__(self, nodelist, heading):
        self.nodelist = nodelist
        self.heading = heading

    def render(self, context):
        text = self.nodelist[0].render(context)
        output = """<div class="sticky-note">
        <div class="text">
            <b class="heading">{}</b>
            {}
        </div>
    </div>""".format(self.heading[1:-1], text)
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
        output = "<div class='spoiler' style='display:{}'>{}</div>".format(self.display, text)
        return output


@register.simple_tag(takes_context=True)
def model_block(context, item, view="detailed", template_view=None, *args, **kwargs):
    if context["request"]:
        item.init_model_block_context(view, request=context["request"], show_staff=context["request"].session.get("SHOW_STAFF", False), *args, **kwargs)
    else:
        item.init_model_block_context(view, request=context["request"], show_staff=False, *args, **kwargs)
    context = item.context
    if template_view is None:
        template_view = view
    return render_to_string("museum_site/subtemplate/model-block-{}.html".format(template_view.replace("_", "-")), context)


@register.simple_tag(takes_context=True)
def queryset_to_model_blocks(context, items, view="detailed", auto_wrap=True, *args, **kwargs):
    output = ""

    if auto_wrap and items:
        if view == "list":
            output += "<table>\n"
            output += items[0].table_header()
        elif view == "gallery":
            output += "<div class='gallery-frame'>\n"

    for i in items:
        output += model_block(context, i, view, *args, **kwargs) + "\n"

    if auto_wrap and items:
        if view == "list":
            output += "</table>"
        elif view == "gallery":
            output += "</div>\n"

    return mark_safe(output + "\n")
