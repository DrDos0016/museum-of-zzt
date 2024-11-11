import { ASCII } from "./core.js";
import { PString } from "./core.js";

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
        this.initial_content = ""; // HTML included in envelope
        this.initial_query_string = "";
        this.supported_file = true; // A disclaimer will be added for reparsed unsupported files

        this.pos = 0;
        this.data = null; // DataView for reading
        this.envelope_id = null; // String to identify HTML for envelope

        this.tabs = [];
        this.default_tab = null;
        this.config_fields = [];
    }

    static initial_config = {};

    async render() {
        console.log("CALLED HANDLER.RENDER()");
        this.deactivate_active_envelopes();
        this.set_tabs();

        this.create_envelope();
        if (! this.parsed)
        {
            this.parse_bytes();
            this.parsed = true;
        }
        let ready = await this.write_html();
        $(this.envelope_id).addClass("active");
    }

    set_tabs()
    {
        $("#tabs").html("");
        for (let idx = 0; idx < this.tabs.length; idx++)
        {
            let tab = this.tabs[idx];
            if (tab.shortcut)
                $("#tabs").append(`<div name="${tab.name}" data-shortcut="${tab.shortcut}">${tab.text}</div>`);
            else
                $("#tabs").append(`<div name="${tab.name}">${tab.text}</div>`);
        }
    }

    deactivate_active_envelopes()
    {
        $(".envelope.active").removeClass("active");
        $("#tabs .active").removeClass("active");
        $("#details .active").removeClass("active");
    }

    create_envelope() {
        if (! this.envelope_id)
        {
            this.envelope_id = "#envelope-" + this.fvpk;
            console.log("CREATING ENVELOPE", this.envelope_id);
            $("#fv-main").append(`<div class="envelope envelope-${this.envelope_css_class}" id="envelope-${this.fvpk}">${this.initial_content}</div>`);
        }
    }

    write_html() {
        console.log(`WARNING -- No write_html function exists for class ${this.name}!`);
        return true;
    }

    write_targets(targets)
    {
        for (let idx = 0; idx < targets.length; idx++)
        {
            $(targets[idx].target).html(targets[idx].html);
        }
    }

    parse_bytes() {
        this.parsed = true;
        return true;
    }

    read_Ascii(len)
    {
        try {
            var output = Array.from(this.bytes.slice(this.pos, this.pos+len)).map((x) => ASCII[x]).join("");
        } catch (e) {
            var output = [0];
        }
        this.pos += len;
        return output;
    }

    read_Uint8()
    {
        try {
            var output = this.data.getUint8(this.pos);
        } catch (e) {
            var output = 0;
        }
        this.pos += 1;
        return output;
    }

    read_Int16()
    {
        try {
            var output = this.data.getInt16(this.pos, true);
        } catch (e) {
            var output = 0;
        }
        this.pos += 2;
        return output;
    }

    read_PString(max_length)
    {
        // Reads 1 byte of current string length, and max_length bytes of string text
        let current_length = this.read_Uint8();
        return new PString(this.read_Ascii(max_length), current_length, max_length);
    }

    get_ext_from_filename(filename)
    {
        if (! filename)
            filename = "UHHH?.FAKE";
        let components = filename.split(".");
        let ext = "." + components[components.length - 1].toUpperCase();
        return ext;
    }

    close()
    {
        console.log("Base handler CLOSE()");
        $(this.envelope_id).removeClass("active");
    }

    display_tab(tab)
    {
        $(`#tabs .active`).removeClass("active");
        $(`#details .active`).removeClass("active");
        $(`#tabs div[name=${tab}]`).addClass("active");
        $(`#details #${tab}`).addClass("active");
    }

    get_config_key_for_handler()
    {
        return this.name.replaceAll(" ", "_").toLowerCase();
    }

    get_config_field(field)
    {
        let widget = "";
        let full_setting = this.get_config_key_for_handler() + "." + field.config_setting;
        let current_value = this.resolve_config_path(field.config_setting);

        if (field.widget == "select")
        {
            let options_html = "";
            for (let idx=0; idx < field.options_data.length; idx++)
            {
                let option = field.options_data[idx];
                options_html += `<option value="${option.value}"${(current_value == option.value) ? " selected" : ""}>${option.text}${option.default ? "*" : ""}</option>\n`;
            }

            widget = `<select id="${full_setting}" data-config="${full_setting}" data-type="${field.data_type}" data-reparse="${field.reparse}">
                ${options_html}
            </select>\n`;
        }

        let field_html = `<div class="field-wrapper">
            <label>${field.label_text}:</label>
            <div class="field-value">
                ${widget}
            </div>
            <p class="field-help">${field.help_text}</p>
        </div>\n`;

        return field_html;
    }

    resolve_config_path(setting)
    {
        let components = setting.split(".");
        // TODO: This seems like it's a dumb way to do this. -- Note this isn't identical to the other dumb time I do this in in file_viewer.js
        switch (components.length) {
            case 4:
                return this.config[components[0]][components[1]][components[2]][components[3]];
            case 3:
                return this.config[components[0]][components[1]][components[2]];
            case 2:
                return this.config[components[0]][components[1]];
            case 1:
                return this.config[components[0]];
        }
        console.log("ERROR: Invalid config path");
    }

}
