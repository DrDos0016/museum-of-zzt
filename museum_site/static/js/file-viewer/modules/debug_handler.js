import { Handler } from "./handler.js";

export class Debug_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Debug Handler";
        this.envelope_css_class = "fvdebug";
        this.fv_files = {};
        this.preview_image_url = "";
        this.description = "";
        this.envelope_id = ""; // Generate when needed, not in advance
        this.zip_comment = "";
    }

    parse_bytes() {
        // Overview has no bytes, but this seems like a good place to pull data from the pre-rendered HTML
        console.log("Parsing the so called bytes");
        return false;
    }

    write_html() {
        console.log("DEBUG HTML generation");

        let targets = [
            {"target": this.envelope_id, "html": this.generate_overview()},
        ];

        this.write_targets(targets);
        return true;
    }

    generate_overview()
    {
        let output = `<input type="button" id="debug-ingest-button" value="Ingest Debug Data"><hr><div id="debug-wrapper"></div>`;
        return output;
    }
}
