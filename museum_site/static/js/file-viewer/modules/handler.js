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

        this.pos = 0;
        this.data = null; // DataView for reading
        this.envelope_id = null; // String to identify HTML for envelope
    }

    static initial_config = {};

    async render() {
        console.log("CALLED HANDLER.RENDER()");
        this.deactivate_active_envelopes()

        this.create_envelope();
        if (! this.parsed)
        {
            this.parse_bytes();
            this.parsed = true;
        }
        let ready = await this.write_html();
        $(this.envelope_id).addClass("active");
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
        console.log("TAB", tab);
        $(`#tabs .active`).removeClass("active");
        $(`#details .active`).removeClass("active");
        $(`#tabs div[name=${tab}]`).addClass("active");
        $(`#details #${tab}`).addClass("active");
    }

    /*history_add()
    {
        console.log("HISTORY ADD IS BEING CALLED");
        if (this.filename == "Overview")
        {
            history.pushState({}, "", ("" + window.location).split("?")[0]);
            return;
        }

        let state = {"open_file": this.filename}
        let url = "?file=" + encodeURIComponent(this.filename);

        if (this.selected_board !== undefined)
        {
            state["selected_board"] = this.selected_board;
            url += "&board=" + this.selected_board;

            //console.log("A:", url);
            //console.log("B:", initial_query_string);
            if (url == ("?" + initial_query_string))
            {
                initial_query_string = ""
                return false;

            }
            //if (window.location.hash)
                //url += window.location.hash;
        }
        console.log("Pushing History URL", url, "state:", state);
        history.pushState(state, "", url);
    }*/
}
