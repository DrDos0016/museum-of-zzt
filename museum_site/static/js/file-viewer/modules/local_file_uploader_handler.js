import { Handler } from "./handler.js";

export class Local_File_Uploader_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Local File Uploader Handler";
        this.envelope_css_class = "local";
        this.fv_files = {};
    }

    parse_bytes() {
        return false;
    }

    write_html() {
        console.log("Local File HTML generation");

        let targets = [
            {"target": this.envelope_id, "html": this.generate_local_form()},
        ];

        this.write_targets(targets);
        return true;
    }

    generate_local_form()
    {
        let output = `<div>
        <input type="file" name="file_load_widget"><input id="file-load-submit" type="button" value="Load File"> - Load a zip/zzt/whatever
        </div>`;
        return output;
    }
}
