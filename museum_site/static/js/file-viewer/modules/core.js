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
        return this.value.slice(0, this.length);
    }

    revealed_string()
    {
        return this.value.slice(0, this.length) + "<span style='color:#A00'>" + this.value.slice(this.length, this.max_length) + "</span>";
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
