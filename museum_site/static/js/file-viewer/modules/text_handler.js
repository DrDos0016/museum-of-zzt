import { ASCII } from "./core.js";
import { Handler } from "./handler.js";

export class Text_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Text Handler";
        this.envelope_css_class = "text";
        this.encoding = "utf-8"; // utf-8, ascii

        this.available_encodings = ["utf-8", "ascii", "ASCII (Mapping)"];

        this.extension_based_initialization();
    }

    parse_bytes() {
        console.log("Parse bytes for text with encoding:", this.encoding);
        this.pos = 0;

        if (this.encoding == "ASCII (Mapping)")
        {
            this.encoded_text = Array.from(this.bytes.slice(this.pos, this.pos+this.bytes.byteLength)).map((x) => ASCII[x]).join("").replaceAll("♪◙", "\r\n").replaceAll("○", "\t");
        }
        else
        {
            this.encoded_text = new TextDecoder(this.encoding).decode(this.bytes);
        }
    }

    generate_html() {
        console.log("Text file html generation");
        let output = `<div class="handler-controls"><label>Encoding: <select name='fv-option' data-fv_func='set_encoding'>`
        for (var idx = 0; idx < this.available_encodings.length; idx++)
        {
            output += `<option${this.encoding == this.available_encodings[idx] ? ' selected' : ''}>${this.available_encodings[idx]}</option>\n`;
        }
        output += `</select></label></div><pre class="cp437">${this.encoded_text}</pre>`;
        return output;
    }

    set_encoding(encoding)
    {
        this.encoding = encoding;
        this.parse_bytes();
        this.render();
    }

    extension_based_initialization()
    {
        if (this.ext == ".DOC")
        {
            console.log("Auto .DOC settings");
        }
    }
}
