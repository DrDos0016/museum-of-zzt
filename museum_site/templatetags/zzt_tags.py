import os

from django import template
from django.template import Library
from django.utils.safestring import mark_safe
from django.conf import settings

register = Library()


@register.tag(name="scroll")
def scroll(parser, token):
    nodelist = parser.parse(('endscroll',))
    parser.delete_first_token()
    return ZztScroll(nodelist)


class ZztScroll(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        raw = self.nodelist.render(context)
        output = "<div class='zzt-scroll'>\n"

        raw = raw.split("\n")

        if raw[0] != "" and raw[0][0] == "@":
            output += "<div class='name'>" + raw[0][1:] + "</div>\n"
        else:
            output += "<div class='name'>Interaction</div>\n"

        output += "<div class='content'>\n"

        # Header dots
        output += "  •    •    •    •    •    •    •    •    •<br>\n"

        for line in raw[1:]:
            if line and line[0] == "$":
                output += "<div class='c white'>" + line[1:] + "</div>\n"
            elif line and line[0] == "!":
                output += ("<div class='hypertext'>" + line.split(";", 1)[-1] +
                           "</div>\n")
            else:
                output += line + "<br>\n"

        if raw[-1] == "":  # Strip trailing empty string resulting in newline
            output = output[:-5]

        # Footer dots
        output += "  •    •    •    •    •    •    •    •    •<br>\n"
        output += "</div>\n</div>\n"

        # Fix spacing
        output = output.replace("  ", "&nbsp; ")
        return output


@register.simple_tag()
def zzt_img(source, shorthand="", alt="", tl="", br="", css=""):
    has_coords = True if tl != "" and br != "" else False

    if source.find(".") == -1:  # Default extension
        source = source + ".png"

    if shorthand != "":
        shorthand = " zzt-" + shorthand

    # Custom cropping (should not be mixed with shorthand)
    if has_coords:
        # Convert to (0,0) based tuples
        tl = (int(tl.split(",")[0]) - 1, int(tl.split(",")[1]) - 1)
        br = (int(br.split(",")[0]) - 1, int(br.split(",")[1]) - 1)

        left = tl[0] * 8
        top = tl[1] * 14
        width = (br[0] - tl[0] + 1) * 8
        height = (br[1] - tl[1] + 1) * 14

        # Generate cropped CSS for image
        img_css = "position:relative;left:-{}px;".format(left)
        img_css += "top:-{}px".format(top)

        # Adjust dimensions of container div
        css += "width:{}px;height:{}px".format(width, height)
    else:
        img_css = ""

    if alt == "":
        alt = os.path.splitext(os.path.basename(source))[0]

    # Crate the div/img tags
    div = "div class='zzt-img{}' style='{}'".format(shorthand, css)

    img = "img src='{}{}' class='{}' alt='{}' title='{}'".format(
        settings.STATIC_URL,
        source,
        shorthand[1:],
        alt,
        alt,
    )

    if img_css:
        img = img + " style='{}'".format(img_css)

    return mark_safe("<" + div + "><" + img + "></div>\n")
