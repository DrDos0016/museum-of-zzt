import { Handler } from "./handler.js";
import { Text_Handler } from "./text_handler.js";

export class Unsupported_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Unsupported Handler";
        this.envelope_css_class = "unsupported";
    }

    generate_html() {
        let output = "<p><b>This file is not supported for in-browser rendering.</b></p>";

        output += `<p>Files of type <span class="keyword">${this.ext}</span> do not have any defined handler to display them.</p>`;
        output += `<p>You may <span>Force this file to be treated as text</span></p>`;
        output += `<p>You may <span class="jsLink fv-ui" data-fv_func="reparse_active_file_as_text">Load this file as a text file</span> - This may allow some data to be read.</p>`;

        return [{"target": this.envelope_id, "html": output}];
    }
}
