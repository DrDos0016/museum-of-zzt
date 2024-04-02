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

    debug()
    {
        return "<div class='mono'><span>" + this.value.slice(0, this.length) + "</span><span style='color:#A00'>" + this.value.slice(this.length) + "</span></div>";
    }
}
