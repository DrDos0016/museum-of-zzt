export let ASCII = "\u0000☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼ !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~⌂ÇüéâäàåçêëèïîìÄÅÉæÆôöòûùÿÖÜ¢£¥₧ƒáíóúñÑªº¿⌐¬½¼¡«»░▒▓│┤╡╢╖╕╣║╗╝╜╛┐└┴┬├─┼╞╟╚╔╩╦╠═╬╧╨╤╥╙╘╒╓╫╪┘┌█▄▌▐▀αßΓπΣσµτΦΘΩδ∞φε∩≡±≥≤⌠⌡÷≈°∙·√ⁿ²■\u00A0";

export class PString
{
    constructor(value, current_length, max_length)
    {
        this.value = value;
        this.length = current_length;
        this.max_length = max_length;
    }

    toString()
    {
        return escape_html(this.value.slice(0, this.length));
    }

    revealed_string()
    {
        return escape_html(this.value.slice(0, this.length)) + "<span class='string-overrun'>" + escape_html(this.value.slice(this.length, this.max_length)) + "</span>";
    }
}

export let KEY = {
    "NP_PLUS": 107, "NP_MINUS": 109,
    "NP_UP": 104, "NP_DOWN": 98, "NP_RIGHT": 102, "NP_LEFT": 100,
    "PLUS": 61, "MINUS": 173,
    "B": 66, "E": 69, "J": 74, "K": 75, "P": 80, "S": 83, "W": 87,
};

export function padded(val, length=2, char="0")
{
    return ("" + val).padStart(length, char);
}

export function escape_html(text)
{
    console.log("ESCAPING", text);
    text = text.replaceAll("<", "&lt;").replaceAll(">", "&gt;");
    return text;
}

export function get_mouse_coordinates(e, relative_to_element=null, zoom=1, border_compensation=true)
{
    // TODO no reason to return anything here but X/Y coords
    let output = {
        "page_x": e.pageX, "page_y": e.pageY, "relative_to": relative_to_element,
        "page_scroll_top": document.querySelector("html").scrollTop, "page_scroll_left": document.querySelector("html").scrollLeft,
    };
    let element = (relative_to_element) ? $(relative_to_element)[0] : $("html")[0];
    let rect = element.getBoundingClientRect();

    output["x"] = e.pageX - rect.left - document.querySelector("html").scrollLeft;
    output["y"] = e.pageY - rect.top - document.querySelector("html").scrollTop;

    if (border_compensation && relative_to_element)
    {
        let border_w = parseInt($(relative_to_element).css("border-left-width").replace("px", ""));
        let border_h = parseInt($(relative_to_element).css("border-top-width").replace("px", ""));
        output["x"] -= (border_w * zoom);
        output["y"] -= (border_h * zoom);
    }
    return output;
}
