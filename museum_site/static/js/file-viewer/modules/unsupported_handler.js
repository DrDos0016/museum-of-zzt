import { Handler } from "./handler.js";
import { Text_Handler } from "./text_handler.js";

export class Unsupported_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Unsupported Handler";
        this.envelope_css_class = "unsupported";

        this.tabs = [
            {"name": "preferences", "text": "Preferences"},
        ];
        this.default_tab = "preferences";
    }

    write_html() {
        let output = "<div class='fv-disclaimer'><p><b>This file does not support in-browser rendering.</b></p>";

        output += `<p>Files of type <span class="keyword">${this.ext}</span> do not have any defined handler to display them.</p>`;
        output += `<p>You can use the options below to force the file to be reated as a text file, which in some circumstances may allow some data to be read.</p>`;
        output += "</div>";

        let targets = [
            {"target": this.envelope_id, "html": output},
            {"target": "#preferences", "html": this.get_preferences()},
        ];
        this.write_targets(targets);
        this.display_tab(this.default_tab);
        return true;
    }

    get_preferences()
    {
        let output = "";

        output += `<div class="field-wrapper">
            <label for="">Force Parsing As Text:</label>
            <div class="field-value"><button type="button" class="reparse-file-button">Reparse File</button></div>
            <p class="field-help">Force this file to be treated as a text file. This may result in garbage data being displayed.</p>
        </div>`;
        return output;
    }
}
