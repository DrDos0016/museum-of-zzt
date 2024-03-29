import { ASCII } from "./core.js";

export class Handler
{
    constructor(fvpk, filename, bytes, meta) {
        this.name = "Base Handler";
        this.fvpk = fvpk;
        this.filename = filename;
        this.ext = this.get_ext_from_filename(filename);
        this.bytes = bytes; // Bytearray of 8-bitvalues
        this.meta = meta; // Metadata
        this.envelope_css_class = "base";

        this.pos = 0;
        this.data = null; // DataView for reading
        this.envelope_id = null; // String to identify HTML for envelope

    }

    render() {
        $(".envelope.active").removeClass("active");

        this.create_envelope();
        if (! this.parsed)
        {
            this.parse_bytes();
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

    parse_bytes() {
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

    get_ext_from_filename(filename)
    {
        let components = filename.split(".");
        let ext = "." + components[components.length - 1].toUpperCase();
        return ext;
    }
}
