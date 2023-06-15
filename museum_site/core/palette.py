from django.template.loader import render_to_string

""" Functions for parsing custom palettes """


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

    for v in upal_vals:
        colors.append(upal_to_rgb(v))

    context["table_rows"] = get_table_rows(colors)

    return render_to_string("museum_site/blocks/fv-palette.html", context)


def parse_pal(pal):
    context = {}
    colors = []

    for i in range(0, 48, 3):
        triplet = (pal[i], pal[i+1], pal[i+2])
        colors.append(triplet)

    context["table_rows"] = get_table_rows(colors)

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


def get_table_rows(colors):
    return [
        {"css_bg": "ega-black-bg", "color": "Black", "custom": colors[0], "hex": color_to_hex_str(colors[0])},
        {"css_bg": "ega-darkblue-bg", "color": "Dark Blue", "custom": colors[1], "hex": color_to_hex_str(colors[1])},
        {"css_bg": "ega-darkgreen-bg", "color": "Dark Green", "custom": colors[2], "hex": color_to_hex_str(colors[2])},
        {"css_bg": "ega-darkcyan-bg", "color": "Dark Cyan", "custom": colors[3], "hex": color_to_hex_str(colors[3])},
        {"css_bg": "ega-darkred-bg", "color": "Dark Red", "custom": colors[4], "hex": color_to_hex_str(colors[4])},
        {"css_bg": "ega-darkpurple-bg", "color": "Dark Purple", "custom": colors[5], "hex": color_to_hex_str(colors[5])},
        {"css_bg": "ega-darkyellow-bg", "color": "Dark Yellow", "custom": colors[6], "hex": color_to_hex_str(colors[6])},
        {"css_bg": "ega-gray-bg", "color": "Gray", "custom": colors[7], "hex": color_to_hex_str(colors[7])},
        {"css_bg": "ega-darkgray-bg", "color": "Dark Gray", "custom": colors[8], "hex": color_to_hex_str(colors[8])},
        {"css_bg": "ega-blue-bg", "color": "Blue", "custom": colors[9], "hex": color_to_hex_str(colors[9])},
        {"css_bg": "ega-green-bg", "color": "Green", "custom": colors[10], "hex": color_to_hex_str(colors[10])},
        {"css_bg": "ega-cyan-bg", "color": "Cyan", "custom": colors[11], "hex": color_to_hex_str(colors[11])},
        {"css_bg": "ega-red-bg", "color": "Red", "custom": colors[12], "hex": color_to_hex_str(colors[12])},
        {"css_bg": "ega-purple-bg", "color": "Purple", "custom": colors[13], "hex": color_to_hex_str(colors[13])},
        {"css_bg": "ega-yellow-bg", "color": "Yellow", "custom": colors[14], "hex": color_to_hex_str(colors[14])},
        {"css_bg": "ega-white-bg", "color": "White", "custom": colors[15], "hex": color_to_hex_str(colors[15])},
    ]


def color_to_hex_str(color):
    hex_r = ("0" + str(hex(color[0]))[2:])[-2:]
    hex_g = ("0" + str(hex(color[1]))[2:])[-2:]
    hex_b = ("0" + str(hex(color[2]))[2:])[-2:]
    return "#{}{}{}".format(hex_r, hex_g, hex_b).upper()
