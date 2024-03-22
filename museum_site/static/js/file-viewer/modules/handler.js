import { ASCII } from "./core.js";

export class Handler
{
    constructor(fvpk) {
        this.name = "Base Handler";
        this.envelope_css_class = "base";
        this.fvpk = fvpk;
        this.pos = 0;
        this.bytes = null; // Bytearray of 8-bitvalues
        this.data = null; // DataView for reading
        this.envelope_id = null; // String to identify HTML for envelope
    }

    render(bytes) {
        $(".envelope.active").removeClass("active");

        this.create_envelope();
        if (! this.parsed)
        {
            this.parse_bytes(bytes);
            this.parsed = true;
        }
        let html = this.generate_html();

        this.display_envelope(html);
    }

    create_envelope() {
        if (! this.envelope_id)
        {
            this.envelope_id = "#envelope-" + this.fvpk;
            $("#fv-main").append(`<div class="envelope envelope-${this.envelope_css_class}" id="envelope-${this.fvpk}"></div>`);
        }
    }

    generate_html() {
        return `<b>No custom HTML function exists for class ${this.name}!</b>`;
    }

    display_envelope(html)
    {
        $(this.envelope_id).html(html);
        $(this.envelope_id).addClass("active");
    }

    parse_bytes(bytes) {
        this.parsed = true;
        return true;
    }

    read_Ascii(len)
    {
        let output = Array.from(this.bytes.slice(this.pos, this.pos+len)).map((x) => ASCII[x]).join("");
        this.pos += len;
        return output;
    }

    read_Uint8()
    {
        let output = this.data.getInt8(this.pos);
        this.pos += 1;
        return output;
    }

    read_Int16()
    {
        let output = this.data.getInt16(this.pos, true);
        this.pos += 2;
        return output;
    }
}
