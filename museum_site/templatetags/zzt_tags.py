import os

from django import template
from django.template import Library
from django.utils.safestring import mark_safe
from django.conf import settings

register = Library()


@register.simple_tag()
def char(num=2, fg="white", bg="black", scale=2, mode="image"):
    colors = [
        "black", "darkblue", "darkgreen", "darkcyan", "darkred", "darkpurple", "darkyellow", "gray",
        "darkgray", "blue", "green", "cyan", "red", "purple", "yellow", "white", "transparent"
    ]
    CP437_TO_UNICODE = (
    0, 9786,  9787, 9829, 9830, 9827, 9824, 8226,
    9688, 9675, 9689, 9794, 9792, 9834, 9835, 9788,
    9658, 9668, 8597, 8252, 182, 167, 9644, 8616,
    8593, 8595,8594, 8592, 8735, 8596, 9650, 9660,
    32, 33, 34, 35, 36, 37, 38, 39,
    40, 41, 42, 43, 44, 45, 46, 47,
    48, 49, 50, 51, 52, 53, 54, 55,
    56, 57, 58, 59, 60, 61, 62, 63,
    64, 65, 66, 67, 68, 69, 70, 71,
    72, 73, 74, 75, 76, 77, 78, 79,
    80, 81, 82, 83, 84, 85, 86, 87,
    88, 89, 90, 91, 92, 93, 94, 95,
    96, 97, 98, 99, 100, 101, 102, 103,
    104, 105, 106, 107, 108, 109, 110, 111,
    112, 113, 114, 115, 116, 117, 118, 119,
    120, 121, 122, 123, 124, 125, 126, 8962,
    199, 252, 233, 226, 228, 224, 229, 231,
    234, 235, 232, 239, 238, 236, 196, 197,
    201, 230, 198, 244, 246, 242, 251, 249,
    255, 214, 220, 162, 163, 165, 8359, 402,
    225, 237, 243, 250, 241, 209, 170, 186,
    191, 8976, 172, 189, 188, 161, 171, 187,
    9617, 9618, 9619, 9474, 9508, 9569, 9570, 9558,
    9557, 9571, 9553, 9559, 9565, 9564, 9563, 9488,
    9492, 9524, 9516, 9500, 9472, 9532, 9566, 9567,
    9562, 9556, 9577, 9574, 9568, 9552, 9580, 9575,
    9576, 9572, 9573, 9561, 9560, 9554, 9555, 9579,
    9578, 9496, 9484, 9608, 9604, 9612, 9616, 9600,
    945, 223, 915, 960, 931, 963, 181, 964,
    934, 920, 937, 948, 8734, 966, 949, 8745,
    8801, 177, 8805, 8804, 8992, 8993, 247, 8776,
    176, 8729, 183, 8730, 8319, 178, 9632, 160
    )
    CHARSET_WIDTH = 1024
    CHARSET_HEIGHT = 448

    num = int(num)

    if num < 0 or num > 255:
        num = 2
    if fg not in colors:
        fg = "white"
    if bg not in colors:
        bg = "darkblue"

    if mode == "text":
        output = "<span class='cp437 ega-{} ega-{}-bg'{}>&#{};</span>"
        if scale != 1:
            scale = " style='font-size:{}px'".format(scale * 14)

        return mark_safe(output.format(fg, bg, scale, CP437_TO_UNICODE[num]))
    else:  # image
        output = "<div class='ascii-char-image ega-{}-bg' title='&#{};' style='width:{}px;height:{}px;background-position:{}px {}px;background-size:{}px {}px;image-rendering: pixelated;'></div>"

        # Adjust position by character
        row = num // 16
        col = num % 16
        pos_x = -8 * col
        pos_y = -14 * row

        # Adjust position by foreground color
        color = colors.index(fg)
        if color < 8:
            pos_x -= color * 128
        else:
            pos_x -= (color - 8) * 128
            pos_y -= 224


        # Adjust position by scale
        pos_x = pos_x * scale
        pos_y = pos_y * scale
        size_x = CHARSET_WIDTH * scale
        size_y = CHARSET_HEIGHT * scale

        output = output.format(bg, CP437_TO_UNICODE[num], 8 * scale, 14 * scale, pos_x, pos_y, size_x, size_y)
        return mark_safe(output)


@register.simple_tag()
def hyperlink(text, inline=False):
    if inline:
        output = "<span class='cl-hyperlink'>{}</span>"
    else:
        output = "<div class='cl-hyperlink'>{}</div>"

    output = output.format(text)
    return mark_safe(output + "\n")


@register.tag(name="message")
def message(parser, token):
    nodelist = parser.parse(('endmessage',))
    parser.delete_first_token()

    # Defaults
    color = "auto"
    scrolling = False

    for arg in token.contents.split():
        if arg == "scrolling":
            scrolling = True
        elif arg in ["yellow", "purple", "red", "cyan", "green", "blue", "white"]:
            color = arg


    return ZztMessage(nodelist, color, scrolling)


class ZztMessage(template.Node):
    def __init__(self, nodelist, color="auto", scrolling=False):

        # Horrible legacy code
        if "|" in color:
            args = color.split("|")
            color = args[0]
            scrolling = args[1] if len(args) > 1 else False

        self.nodelist = nodelist
        self.color_list = ["yellow", "purple", "red", "cyan", "green", "blue", "white",]
        self.color = color
        self.scrolling = scrolling
        if self.color == "auto":
            self.active_color = self.color_list[0]
        else:
            self.active_color = color
        self.color_idx = self.color_list.index(self.active_color)

    def advance_color(self):
        if self.color != "auto":
            return False
        self.color_idx += 1
        if self.color_idx >= len(self.color_list):
            self.color_idx = 0
        self.active_color = self.color_list[self.color_idx]
        return True

    def render(self, context):
        raw = self.nodelist.render(context)
        lines = raw.replace("\r\n", "\n").split("\n")


        if self.scrolling:
            output = "<div class='zzt-txt-message scrolling'>\n"
        else:
            output = "<div class='zzt-txt-message'>\n"

        if lines[-1] == "":
            lines.pop()

        if lines[0].lstrip() == "":
            lines = lines[1:]

        for line in lines:
            output += "<span class='{}'>{}</span><br>".format(self.active_color, line)
            if line == "":
                self.advance_color()
        output += "</div>"
        return output


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

        if not str(raw).strip():
            raw = ["", "TODO: SCROLL HAS NO TEXT"]  # Expected TODO usage.
        else:
            raw = raw.split("\n")


        if raw[0] == "" and raw[1][0] == "@":  # It's okay to start on the second line
            raw = raw[1:]
        if raw[0] != "" and raw[0][0] == "@":
            output += "<div class='name'>" + raw[0][1:] + "</div>\n"
        else:
            output += "<div class='name'>Interaction</div>\n"

        output += "<div class='content'>\n"


        # Pad short scrolls with blank lines
        output += "<br>\n" * (10 - len(raw))
        output += "  •    •    •    •    •    •    •    •    •<br>\n"

        # Header dots
        for line in raw[1:]:
            if line and line[0] == "$":
                output += "<div class='white'>" + line[1:] + "</div>\n"
            elif line and line[0] == "!":
                output += ("<div class='hypertext'>" + line.split(";", 1)[-1] +
                           "</div><br>\n")
            else:
                output += "<span class='plaintext'>" + line + "</span><br>\n"

        if raw[-1] == "":  # Strip trailing empty string resulting in newline
            output = output[:-5]

        # Footer dots
        output += "  •    •    •    •    •    •    •    •    •<br>\n"
        output += "</div>\n</div>\n"

        # Fix spacing
        output = output.replace("  ", "&nbsp;&nbsp;")
        return output


@register.simple_tag()
def zzt_img(*args, **kwargs):
    # Combine basic args into the image path
    if len(args) == 1:
        source = args[0]
    elif len(args) >= 2 and args[1][-4:].lower() in [".png", ".gif", ".jpg"]:
        source = os.path.join(args[0], args[1])


    # Pull kwargs
    shorthand = kwargs.get("shorthand", kwargs.get("sh", ""))
    alt = kwargs.get("alt", "")
    tl = kwargs.get("tl", "")
    br = kwargs.get("br", "")
    css = kwargs.get("css", "")
    message_crop = kwargs.get("mcrop", kwargs.get("mc", ""))
    caption = kwargs.get("cap", "")

    has_coords = True if tl and br else False

    if shorthand:
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
        img_css = "max-width:none;position:relative;left:-{}px;".format(left)
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

    crop = ""
    if "CROP" in args:
        crop = "<div class='debug-crop'>CROP</div>"

    output = "<{}><{}></div>{}\n".format(div, img, crop)

    # Attach a 2nd crop with the message text if requested
    if message_crop:
        output = mark_safe("<{}><{}></div>\n".format(div, img, crop))
        if kwargs.get("mcrop"):
            del kwargs["mcrop"]
        if kwargs.get("mc"):
            del kwargs["mc"]
        output+= zzt_img(source, sh="message")

    if caption:
        output += '<div class="img-caption">{}</div>'.format(caption)
    return mark_safe(output)
