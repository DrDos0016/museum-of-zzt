import { ASCII, escape_html } from "./core.js";
import { Handler } from "./handler.js";

export class Text_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Text Handler";
        this.envelope_css_class = "text";

        this.tabs = [
            {"name": "preferences", "text": "Prefs."},
        ];
        this.default_tab = "preferences";

        //this.encoding = "utf-8"; // utf-8, ascii
        this.last_encoding = "utf-8"; // Used to check if a reparse is needed after changing encoding preferences. Starts at default initial config encoding.
        this.available_encodings = ["utf-8", "ascii", "ASCII (Mapping)"];
        this.partially_supported_extensions = [".ANS", ".DOC", ".LNK", ".MS", ".OZ", ".PIF", ".RTF", ".WPS", ".WRI"]; // TODO .ANS is temporary maybe?
        this.extension_based_initialization();
    }

    static initial_config = {
        "renderer": {
            "encoding": "utf-8",
        },
    }

    parse_bytes() {
        this.pos = 0;
        if (this.config && this.config.renderer.encoding == "ascii-mapping")
        {
            this.encoded_text = Array.from(this.bytes.slice(this.pos, this.pos+this.bytes.byteLength)).map((x) => ASCII[x]).join("").replaceAll("♪◙", "\r\n").replaceAll("○", "\t");
            this.last_encoding = this.config.renderer.encoding;
        }
        else
        {
            this.encoded_text = new TextDecoder(this.encoding).decode(this.bytes);
            this.last_encoding = "utf-8"
        }
    }

    write_html() {
        // TODO: REDO THIS MORE LIKE ZZT HANDLER WITH AN ENVELOPE TEMPLATE
        console.log("Text file html generation", this.config);
        if (this.config.renderer.encoding != this.last_encoding)
            this.set_encoding(this.config.renderer.encoding);

        let output = "";
        console.log(this.ext)

        if (this.partially_supported_extensions.indexOf(this.ext) != -1)
            output += `<div class="fv-disclaimer">Files with the extension <span class="keyword">${this.ext}</span> may not be plaintext. You may encounter data not meant to be displayed when viewing this file.</div>`;

        output += `<pre class="cp437">${escape_html(this.encoded_text)}</pre>`;
        let targets = [
            {"target": this.envelope_id, "html": output},
            {"target": "#preferences", "html": this.get_preferences(),},
        ];
        this.write_targets(targets);
        this.display_tab(this.default_tab);
        return true;
    }

    get_preferences()
    {
        let output = "";
        let config_key = this.get_config_key_for_handler();

        output += `<div class="field-wrapper">
            <label for="">Encoding:</label>
            <div class="field-value"><select data-config="${config_key}.renderer.encoding" data-type="str">
                <option value="ascii-mapping"${(this.config.renderer.encoding == 'ascii-mapping' ) ? " selected" : ""}>ASCII (Mapping)</option>
                <option value="utf-8"${(this.config.renderer.encoding == 'utf-8' ) ? " selected" : ""}>UTF-8</option>
            </select></div>
            <p class="field-help">Encoding used for text. Older files are more likely to use ASCII.</p>
        </div>`;

        return output;
    }

    set_encoding(encoding)
    {
        this.last_encoding = encoding;
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
