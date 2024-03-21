import { ASCII } from "./core.js";

export class Handler
{
    constructor() {
        this.name = "Base Handler";
        this.parsed = false;
        this.pos = 0;
        this.bytes = null; // Bytearray of 8-bitvalues
        this.data = null; // DataView for reading
        this.og_prop = "Base OG Property";
    }


    render(fvpk, bytes) {
        console.log("Base handler");
        if (! this.parsed)
            this.parse_bytes(bytes);
    }

    create_envelope(id, kind) {
        $("#fv-main").append(`<div class="envelope envelope-${kind}" id="envelope-${id}">Hello</div>`);
    }

    parse_bytes(bytes) {
        console.log("Base handler parsing bytes");
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
