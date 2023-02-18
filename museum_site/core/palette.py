from PIL import Image

from django.template.loader import render_to_string

""" Functions for parsing .PLD palettes """

def parse_pld(pld):
    context = {}
    colors = []
    upal_vals = []
    indices = [
        0x00, 0x03, 0x06, 0x09, 0x0C, 0x0F, 0x3C, 0x15,
        0xA8, 0xAB, 0xAE, 0xB1, 0xB4, 0xB7, 0xBA, 0xBD,
    ]

    for i in indices:
        upal_val = (pld[i], pld[i+1], pld[i+2])
        upal_vals.append(upal_val)

    # Create swatch
    x = 0
    y = 0
    im = Image.new("RGBA", (256, 16))
    for v in upal_vals:
        colors.append(upal_to_rgb(v))

    context["table_rows"] = [
        {"css_bg": "ega-black-bg", "color": "Black", "custom": colors[0],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[0][2]))[2:]).upper()},
        {"css_bg": "ega-darkblue-bg", "color": "Dark Blue", "custom": colors[1],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[1][2]))[2:]).upper()},
        {"css_bg": "ega-darkgreen-bg", "color": "Dark Green", "custom": colors[2],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[2][2]))[2:]).upper()},
        {"css_bg": "ega-darkcyan-bg", "color": "Dark Cyan", "custom": colors[3],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[3][2]))[2:]).upper()},
        {"css_bg": "ega-darkred-bg", "color": "Dark Red", "custom": colors[4],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[4][2]))[2:]).upper()},
        {"css_bg": "ega-darkpurple-bg", "color": "Dark Purple", "custom": colors[5],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[5][2]))[2:]).upper()},
        {"css_bg": "ega-darkyellow-bg", "color": "Dark Yellow", "custom": colors[6],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[6][2]))[2:]).upper()},
        {"css_bg": "ega-gray-bg", "color": "Gray", "custom": colors[7],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[7][2]))[2:]).upper()},
        {"css_bg": "ega-darkgray-bg", "color": "Dark Gray", "custom": colors[8],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[8][2]))[2:]).upper()},
        {"css_bg": "ega-blue-bg", "color": "Blue", "custom": colors[9],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[9][2]))[2:]).upper()},
        {"css_bg": "ega-green-bg", "color": "Green", "custom": colors[10],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[10][2]))[2:]).upper()},
        {"css_bg": "ega-cyan-bg", "color": "Cyan", "custom": colors[11],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[11][2]))[2:]).upper()},
        {"css_bg": "ega-red-bg", "color": "Red", "custom": colors[12],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[12][2]))[2:]).upper()},
        {"css_bg": "ega-purple-bg", "color": "Purple", "custom": colors[13],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[13][2]))[2:]).upper()},
        {"css_bg": "ega-yellow-bg", "color": "Yellow", "custom": colors[14],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[14][2]))[2:]).upper()},
        {"css_bg": "ega-white-bg", "color": "White", "custom": colors[15],
         "hex": "#" + (str(hex(colors[15][0]))[2:] + str(hex(colors[15][1]))[2:] + str(hex(colors[15][2]))[2:]).upper()},
    ]

    return render_to_string("museum_site/blocks/fv-palette.html", context)

def upal_to_rgb(v):
    (r_comp, g_comp, b_comp) = (v[0], v[1], v[2])

    r_intensity = r_comp / 63
    g_intensity = g_comp / 63
    b_intensity = b_comp / 63

    r = int(r_intensity * 255)
    g = int(g_intensity * 255)
    b = int(b_intensity * 255)

    return (r, g, b)
