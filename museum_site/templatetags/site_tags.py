import pprint
import re
import time

import urllib.parse

import markdown

from django import template
from django.template import Template, Context, Library
from django.template.loader import render_to_string
from django.template.defaultfilters import stringfilter, escape
from django.urls import reverse
from django.utils.safestring import mark_safe

from museum.settings import STATIC_URL
from museum_site.constants import (
    ADMIN_NAME, PROTOCOL, DOMAIN, LANGUAGES
)
from museum_site.core.transforms import qs_manual_order
from museum_site.models import File, Article, Series
from museum_site.templatetags.zzt_tags import char

register = Library()


@register.simple_tag(takes_context=True)
def cl_info(context, pk=None, engine="", emulator=""):
    zfile = File.objects.filter(pk=pk).first()
    if zfile is None:
        zfile = File()
        zfile.id = -1
        zfile.title = "UNKNOWN ZFILE TODO"  # Expected TODO usage.

    zfile.cl_info = {"engine": engine, "emulator": emulator}
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
            commentary = "<p>" + commentary.replace("\r\n\r\n", "</p><p>").replace("\n\n", "</p><p>") + "</p>"

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
        return output.format(debug_classes=debug_classes, material=material, commentary=commentary)


@register.inclusion_tag("museum_site/subtemplate/tag/content-warning.html")
def content_warning(*args, **kwargs):
    return{"kind": "content-warning", "heading": "CONTENT WARNING", "warnings": args, "skip_id": kwargs.get("key", "#end-cw"), "noskip": kwargs.get("noskip")}


@register.simple_tag()
def counter(*args):
    counter_data = {"h": (3, "red"), "a": (132, "darkcyan"), "t": (157, "darkyellow"), "g": (4, "cyan"), "s": (158, "white")}
    output = ""
    for idx in range(0, len(args), 2):
        (char_num, char_fg) = counter_data[args[idx]]
        c = char(num=char_num, fg=char_fg, bg="black", scale=2)
        value = args[idx+1]
        sign = "+" if value > 0 else "-"
        color = "green" if value > 0 else "red"
        output += c + "<span class='cp437 ega-{} ega-black-bg' style='font-size:32px'>{}{}</span> ".format(color, sign, abs(value))

    output = output.strip()
    return mark_safe(output)


@register.simple_tag(name="fn")
def footnote(num=1):
    if num > 0:
        output = "<sup><a href='#fn-{}' id='fnl-{}'>[{}]</a></sup>"
    else:
        num = -1 * num
        output = "<sup><a href='#fnl-{}' id='fn-{}'>[{}]</a></sup>"
    return mark_safe(output.format(num, num, num))


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
    qs = qs_manual_order(File.objects.filter(pk__in=ids), ids)
    files = {}
    for f in qs:
        files[str(f.id)] = f
    for _id in ids:
        if not files.get(str(_id)):
            files[str(_id)] = File(id=-1, title="ERROR: File #{} not found".format(_id), key="NOKEY")
    return files


@register.simple_tag()
def guide_words(qs, *args, **kwargs):
    if len(qs) == 0:
        return ""

    sort = kwargs.get("sort", "")
    location = kwargs.get("location", "top")

    output = """<div class="guide-words">
        <span><a class="left" href="#{}">{}</a></span>
        <span><a class="right" href="#{}">{}</a></span>
    </div>"""

    (first_key, first_value) = qs[0].guide_words(sort)
    (last_key, last_value) = qs[len(qs) - 1].guide_words(sort)
    return mark_safe(output.format(first_key, first_value, last_key, last_value) + "\n")


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


@register.simple_tag(name="image_set", takes_context=True)
def image_set(context, *args, **kwargs):
    path = context.get("path")
    if path:
        if not isinstance(path, str):
            path = path()
    else:
        path = kwargs.get("path", "NO-PATH-FOUND")
    output = "<div class='image-set'>\n"
    if kwargs.get("range") and kwargs.get("prefix"):
        (start, end) = kwargs["range"].split("-")
        args = []
        for x in range(int(start), int(end) + 1):
            args.append("{}-{}.png".format(kwargs["prefix"], x))
    for img in args:
        output += "<img src='{}{}{}' class='zoomable thumbnail'>\n".format(STATIC_URL, path, img)
    output += "</div>\n"
    return mark_safe(output)


@register.filter(name="markdown")
def render_markdown(raw):
    filtered = escape(raw)
    marked = markdown.markdown(filtered)

    # TODO: This should probably be a bit more formal
    matches = re.findall("\|\|", marked)
    spoiler_tag_count = len(matches)
    if spoiler_tag_count % 2 != 0:
        spoiler_tag_count -= 1

    for x in range(0, spoiler_tag_count):
        if x % 2 == 0:
            marked = marked.replace("||", "<span class='spoiler'>", 1)
        else:
            marked = marked.replace("||", "</span>", 1)

    return mark_safe(marked)


@register.simple_tag()
def meta_tags(*args, **kwargs):
    print("META TAG TIME")
    # Default values
    base_url = "{}://{}{}".format(PROTOCOL, DOMAIN, STATIC_URL[:-1])

    if kwargs.get("include_qs"):
        path = kwargs.get("path", "")
    else:
        path = kwargs.get("path", "").split("?")[0]  # Sans QS

    url = base_url + path
    og_default = "pages/og_default.png"
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


@register.simple_tag(takes_context=True)
def model_block(context, item, view="detailed", template_view=None, *args, **kwargs):
    if item in [None, ""]:
        return ""
    item.init_model_block_context(view, request=context["request"], **kwargs)
    if template_view is None:
        template_view = view
    if kwargs.get("alt") and item.title.startswith("ERROR: File #"):
        item.context["title"]["value"] = "<span class='faded'>{}</span>".format(kwargs["alt"])
    return render_to_string("museum_site/subtemplate/model-block-{}.html".format(template_view.replace("_", "-")), item.context)


@register.simple_tag(name="m")
def model_block_link_tag(model_name, identifier, text=None, i=True, *args, **kwargs):
    """ Model Link """
    """ {% m "model_name" <pk/key> "link text" %}"""

    available_models = {"zfile": File, "series": Series, "article": Article}
    error_message = "TODO INVALID MODEL BLOCK LINK TAG [{}][{}]".format(model_name, identifier)

    attr = "pk" if isinstance(identifier, int) else "key"
    try:
        item = available_models[model_name].objects.filter(**{attr: identifier})
    except KeyError:
        return mark_safe(error_message)

    if item:
        item = item.first()
    else:
        return mark_safe(error_message)

    if text is None:
        text = item.title

    if i:
        text = "<i>" + text + "</i>"

    output = "<a href='{}' target='_blank'>{}</a>".format(item.get_absolute_url(), text)

    return mark_safe(output)


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


@register.simple_tag()
def patreon_plug(*args, **kwargs):
    return render_to_string("museum_site/subtemplate/patreon-plug.html", {})


@register.inclusion_tag("museum_site/subtemplate/tag/plug.html")
def plug(service, **kwargs):
    services = {
        "bluesky": {"service": "Bluesky", "icon": "/static/icons/bsky.svg", "text": "Worlds of ZZT on Bluesky"},
        "twitter": {"service": "Twitter", "icon": "/static/icons/plug-twitter.png", "text": "Worlds of ZZT on Twitter"},
        "mastodon": {"service": "Mastodon", "icon": "/static/icons/plug-mastodon.svg", "text": "Worlds of ZZT on Mastodon"},
        "tumblr": {"service": "Tumblr", "icon": "/static/icons/plug-tumblr.png", "text": "Worlds of ZZT on Tumblr"},
        "discord": {"service": "Discord", "icon": "/static/icons/plug-discord.png", "text": "Worlds of ZZT on Discord"},
        "patreon": {"service": "Patreon", "icon": "/static/icons/patreon_logo.png", "text": "Worlds of ZZT on Patreon"},
        "youtube": {"service": "YouTube", "icon": "/static/icons/plug-youtube.png", "text": "Worlds of ZZT on YouTube"},
        "twitch": {"service": "Twitch", "icon": "/static/icons/plug-twitch.png", "text": "Worlds of ZZT on Twitch"},
        "github": {"service": "GitHub", "icon": "/static/icons/GitHub-Mark-32px.png", "text": "Worlds of ZZT on GitHub"},
        "rss": {"service": "RSS", "icon": "/static/icons/rss-large.png", "text": "Worlds of ZZT RSS Feeds"},
    }

    context = services.get(service)
    return context


@register.filter
def qs_sans(raw, args):
    query_dict = raw.copy()

    for key in args.split(","):
        if key in query_dict.keys():
            del query_dict[key]

    query_string = query_dict.urlencode()
    if query_string:
        return "&" + query_string
    return ""


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


@register.simple_tag()
def zfile_citation(zfile, **kwargs):
    """ Returns a string of standard information used in publication packs """
    if not zfile.pk:
        return "“” by X ()"
    else:
        authors_list = zfile.related_list("authors")

    title = '“{}”'.format(zfile.title)
    author = "by {}".format(", ".join(authors_list)) if authors_list != ["Unknown"] else ""
    year = "({})".format(zfile.release_year()) if (zfile.release_date or zfile.year) else ""
    return " ".join([title, author, year])


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


@register.simple_tag()
def nav_action_list(key, condition=None):
    # TEMP LOCATION OF THIS INFORMATION
    actions = []
    if key == "collection":
        actions = [
            {"selected": True if condition.startswith("/collection/browse/") else False, "url": reverse("collection_browse"), "text": "Collection Directory"},
            {"selected": True if condition.startswith("/collection/new/") else False, "url": reverse("collection_new"), "text": "Create Collection"},
            {"selected": True if condition.startswith("/collection/user/") else False, "url": reverse("collection_user"), "text": "Manage Collections"},
            {
                "selected": True if condition.startswith("/collection/on-the-fly-collections/") else False,
                "url": reverse("collection_on_the_fly_collections"), "text": "On The Fly Collections"
            },
        ]
    elif key == "collection-manage":
        actions = [
            {"selected": True if condition in ["add", ""] else False, "url": "?operation=add", "text": "Add Entry"},
            {"selected": True if condition == "remove" else False, "url": "?operation=remove", "text": "Remove Entry"},
            {"selected": True if condition == "arrange" else False, "url": "?operation=arrange", "text": "Arrange Entries"},
            {"selected": True if condition == "edit-entry" else False, "url": "?operation=edit-entry", "text": "Edit Entries"},
        ]
    elif key == "upload":
        actions = [
            {"selected": False, "url": reverse("upload"), "text": "Upload a New File"},
            {"selected": False, "url": reverse("upload_action", "edit"), "text": "Edit An Existing Upload"},
            {"selected": False, "url": reverse("upload_action", "delete"), "text": "Delete An Existing Upload"},
        ]
    elif key == "feedback":
        # TODO: This is hardcoded and needs updating with each tag added to the database
        actions = [
            {"selected": True if condition == "" else False, "url": "?", "text": "All Feedback"},
            {"selected": True if condition == "changelogs" else False, "url": "?filter=changelogs", "text": "Changelogs"},
            {"selected": True if condition == "bugs" else False, "url": "?filter=bugs", "text": "Bug Reports"},
            {"selected": True if condition == "cws" else False, "url": "?filter=cws", "text": "Content Warnings"},
            {"selected": True if condition == "hints" else False, "url": "?filter=hints", "text": "Hints and Solutions"},
            {"selected": True if condition == "reviews" else False, "url": "?filter=reviews", "text": "Reviews"},
            {"selected": True if condition == "toc" else False, "url": "?filter=toc", "text": "Table of Contents"},
        ]
    return render_to_string("museum_site/subtemplate/tag/nav-action-list.html", {"actions": actions})


@register.simple_tag()
def ml(url, text, target="_blank", i=True, *args, **kwargs):
    """ Museum Link - Takes a full URL, strips the domain, adds italicized text and opens in a new tab """
    """ {% ml "http://django.pi:8000/article/view/963/featured-world-the-2021-make-a-neat-zzt-board-contest-jam-type-thing-compilation/" "FW: Neat" %}"""

    if "/" not in url:
        # Treat URL as just a ZFile key
        output_url = "/file/view/{}/".format(url)
    else:
        components = url.replace("http://", "").replace("https://", "").split("/")[1:]
        output_url = "/" + "/".join(components)

    output = '<a href="{}"{}>{}</a>'
    target_string = "target=" + target if target else ""
    output = output.format(output_url, target_string, text)
    if i:
        output = "<i>{}</i>".format(output)
    return mark_safe(output)


@register.inclusion_tag("museum_site/subtemplate/tag/zfile-upload-info.html", takes_context=True)
def zfile_upload_info(context, zfile):
    return {"zfile": zfile, "is_staff": context["request"].user.is_staff}


@register.inclusion_tag("museum_site/subtemplate/tag/youtube-embed.html")
def youtube_embed(video_id, w=960, h=540):
    return {"video_id": video_id, "w": w, "h": h}


@register.tag(name="zzm")
def zzm(parser, token):
    nodelist = parser.parse(('endzzm',))
    parser.delete_first_token()
    kwargs = {}

    str_kwargs = token.split_contents()[1:]
    for param in str_kwargs:
        (k, v) = param.split("=")
        if v.startswith("'") or v.startswith('"'):
            kwargs[k] = v[1:-1]
        else:
            if "." in v:
                kwargs[k] = float(v)
            else:
                kwargs[k] = int(v)
    return ZZM_Player(nodelist, **kwargs)


class ZZM_Player(template.Node):
    def __init__(self, nodelist, **kwargs):
        self.default_volume = "0.5"
        self.default_require_prefix = True
        self.nodelist = nodelist
        self.tag_params = kwargs

    def render(self, context):
        notes = self.nodelist.render(context)
        tag_context = self.tag_params
        if tag_context.get("duration") and tag_context["duration"] != "--:--":
            m, s = tag_context["duration"].split(":")
            s = int(m) * 60 + int(s)
            tag_context["ms"] = s * 1000
        else:
            tag_context["ms"] = 0
        tag_context.setdefault("vol", self.default_volume)
        tag_context.setdefault("require_prefix", self.default_require_prefix)
        tag_context.setdefault("duration", "--:--")
        tag_context.setdefault("vol_percent", int(float(tag_context["vol"]) * 100))

        # Prepare notes
        tag_context["notes"] = ""
        for line in notes.split("\n"):
            tag_context["notes"] += "#play " + line + "\n"
        t = context.template.engine.get_template("museum_site/subtemplate/tag/zzm-player.html")
        return t.render(Context(tag_context, autoescape=context.autoescape))
