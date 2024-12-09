import { Debug_Handler } from "./debug_handler.js";
import { Image_Handler } from "./image_handler.js";
import { Local_File_Uploader_Handler } from "./local_file_uploader_handler.js";
import { Overview_Handler } from "./overview_handler.js";
import { Text_Handler } from "./text_handler.js";
import { Unsupported_Handler } from "./unsupported_handler.js";
import { ZZT_High_Score_Handler, SZZT_High_Score_Handler } from "./high_score_handler.js";
import { SZZT_Handler, ZZT_Handler } from "./zzt_handler.js";

export const EXTENSIONS_IMAGE = [".BMP", ".GIF", ".ICO", ".JPG", ".PNG", ".SVG"];
export const EXTENSIONS_HIGH_SCORE = [".HI", ".MH"];
export const EXTENSIONS_HIGH_SCORE_SZZT = [".HGS"];
export const EXTENSIONS_TEXT = [
"", ".000", ".001", ".002", ".135", ".1ST", ".AC", ".AM", ".AMI", ".ANS", ".APPIMAGE", ".ASC", ".ASM", ".BAS", ".BAT", ".BB",
".BI", ".BIN", ".C", ".CC", ".CD", ".CFG", ".CPP", ".CRD", ".CSS", ".DAT", ".DEF", ".DESKTOP",
".DEU", ".DIZ", ".DOC", ".DOS", ".DOX", ".DS_STORE", ".E", ".EED", ".ENG", ".EPS", ".ERR", ".EX",
".FAQ", ".FLG", ".FRM", ".FYI", ".GITIGNORE", ".GPL3", ".GUD", ".H", ".HLP", ".HTS", ".IN", ".INC", ".INF",
".INI", ".INV", ".JAVA", ".JS", ".JSON", ".KB", ".LIB", ".LICENSE", ".LOG", ".LNK", ".LST", ".LUA",
".M4", ".MAC", ".MACOS", ".MACOS_SDK_EXTRACTOR", ".MAP", ".MD",
".ME", ".MS", ".MSG", ".MUZ", ".NEW", ".NFO", ".NOW", ".OBJ", ".OLF", ".OOP", ".OZ", ".PAR", ".PAS", ".PATCH",
".PIF", ".PLIST", ".PS", ".PY", ".REG", ".RTF", ".ROT13", ".SDI", ".SH", ".SLV", ".SOL", ".SOURCE", ".ST", ".THEME", ".TXT",
".URL", ".WINDOWS", ".WPS", ".WRI", ".XML", ".ZLN", ".ZML", ".ZZL", ".ZZM",
".~~~", ".---",
]
export const EXTENSIONS_ZZT = [".MWZ", ".SAV", ".Z_T", ".ZZT"]; // TODO Super ZZT Saves
export const EXTENSIONS_SZZT = [".SZT"]; // TODO Super ZZT Saves

export class File_Viewer
{
    auto_load_max_size = 2097152;  // Maximum size of a zip file to automatically parse its contents
    //auto_load_max_size = 10;  // Maximum size of a zip file to automatically parse its contents
    fvi_count = 1000;
    zip_file_path = "";
    files = {};
    default_domain = "localhost";
    active_fvpk = "fvpk-overview"; // The FVPK of the currently displayed file
    has_auto_load_target = false;
    auto_load_file_name = "Overview"; // Click overview by default
    scroll_y = window.scrollY;
    configs = {
        "global": {
            "foo": "bar",
            "baz": "bap",
        }
    }; // Configuration data for handlers

    add_file(filename, bytes, meta)
    {
        // Adds a file into the file registry
        let fvpk = "fvpk-" + this.fvi_count;
        this.files[fvpk] = create_handler_for_file(fvpk, filename, bytes, meta);
        if (this.has_auto_load_target && (filename == this.auto_load_filename))
        {
            this.files[fvpk].selected_board = this.auto_load_board;
            //this.files[fvpk].auto_click = window.location.hash;
            //console.log("HASH IS", window.location.hash);
        }
        this.fvi_count++;
        return fvpk;
    }

    render_file_list_item(fvpk)
    {
        // Writes a list item to the page's file list section
        if (this.files[fvpk].filename.indexOf("__MACOSX/") != -1)
            return false;

        $("#file-list").append(
            `<li class="fv-content" data-fvpk="${fvpk}" data-filename="${this.files[fvpk].filename}">${this.files[fvpk].filename}</li>`
        );
    }

    display_file_list()
    {
        // Writes the entire file registry to the page's file list section
        for(let [filename, file] of Object.entries(this.files))
        {
            this.render_file_list_item(filename);
        }
        console.log("============= DONE WITH DFL");
    }

    display_file(fvpk)
    {
        // Displays the file {fvpk}
        console.log("FV wants to display...", fvpk);

        // Close any open file (for now, TODO proper multi-file support)
        let to_close = $(".fv-content.selected").data("fvpk");
        if (to_close)
        {
            this.files[to_close].close();
        }

        // This removes the board list and deselects the file for any expanded files
        $(".fv-content.selected ol").remove();
        $(".fv-content.selected").removeClass("selected");

        $(".fv-content[data-fvpk=" + fvpk + "]").addClass("selected");
        this.push_config(fvpk);
        this.files[fvpk].render();
        this.history_add();
    }

    async reparse_file_as_text()
    {
        let fvpk = this.files[this.active_fvpk].fvpk;
        let filename = this.files[this.active_fvpk].filename;
        let bytes = this.files[this.active_fvpk].bytes;
        let meta = this.files[this.active_fvpk].meta;
        this.files[fvpk] = new Text_Handler(fvpk, filename, bytes, meta);
        this.files[fvpk].config = null; // Clear the Unsupported Handler config
        this.push_config(fvpk);
        await this.files[fvpk].render();
        $(`#envelope-${fvpk}`).removeClass("envelope-unsupported");
        $(`#envelope-${fvpk}`).addClass("envelope-text");
    }

    board_change(new_board_number)
    {
        console.log("CALLING BOARD CHANGE");
        this.files[this.active_fvpk].selected_board = parseInt(new_board_number);
        this.files[this.active_fvpk].render();
    }

    board_title_click(e)
    {
        console.log("-----------------Board title click");
        this.scroll_y = window.scrollY;
        let bn = $(e.currentTarget).data("board-number");
        this.board_change(bn);
        $(window).scrollTop(this.scroll_y);
        this.history_add();
    }

    resort_stats(e)
    {
        console.log("Resorting stats!");
        this.files[this.active_fvpk].update_stat_sorting(e);
    }

    stat_click(e)
    {
        e.preventDefault();
        console.log("STAT CLICK START", $(e.currentTarget));
        let coords = {"x": $(e.currentTarget).data("x"), "y": $(e.currentTarget).data("y")};
        history.replaceState(undefined, undefined, `#${coords.x},${coords.y}`);
        console.log("COORDS?", coords);
        this.files[this.active_fvpk].write_element_info(coords.x, coords.y)
    }

    async stat_match_click(e)
    {
        console.log("STAT MATCH CLICK", e)
        let coord_str = `#${$(e.target).data("x")},${$(e.target).data("y")}`;
        this.files[this.active_fvpk].auto_click = coord_str;
        await this.board_title_click(e);
    }

    code_search(e)
    {
        let query = $("input[name=code-search]").val();
        this.files[this.active_fvpk].code_search(query);
    }

    clear_search(e)
    {
        console.log("Clearing search");
        let active = this.files[this.active_fvpk];
        $("input[name=code-search]").val("");
        active.query = "";
        active.write_targets([{"target": `.fv-content[data-fvpk="${active.fvpk}"]`, "html": active.write_board_list()}]);
    }

    hover_stat_start(e)
    {
        this.files[this.active_fvpk].renderer.crosshair($(e.target).data("x"), $(e.target).data("y"), "on");
    }


    hover_stat_stop(e)
    {
        this.files[this.active_fvpk].renderer.crosshair($(e.target).data("x"), $(e.target).data("y"), "off");
    }

    history_add()
    {
        if (this.files[this.active_fvpk].filename == "Overview" || this.files[this.active_fvpk].filename == "Upload Local File")
            return false;

        let state = {"open_file": this.files[this.active_fvpk].filename, "board": this.files[this.active_fvpk].selected_board};


        console.log("CURRENT STATE", history.state);
        console.log("NEW STATE---", state);

        if (state.board)
            history.pushState(state, "", `?file=${state.open_file}&board=${state.board}`);
        else
            history.pushState(state, "", `?file=${state.open_file}`);

        console.log("History pushed state", state);
        return true;
    }

    push_config(fvpk)
    {
        // Pushing a config
        console.log("Push config", fvpk);
        let config_key = this.files[fvpk].name.replaceAll(" ", "_").toLowerCase();
        if (! this.configs[config_key])  // Create config if not found
        {
            console.log("No config found! Creating new config.");
            this.configs[config_key] = this.files[fvpk].constructor.initial_config;

            // TODO This may be a mess
            if (this.files[fvpk].renderer)
            {
                console.log("FVPK has renderer", fvpk);
                this.configs[config_key]["renderer"] = this.files[fvpk].renderer.constructor.initial_config;
            }
            console.log("Pushed an initial config");
        }

        console.log("NAME HERE", this.files[fvpk].name);

        this.files[fvpk].config = this.configs[config_key];


        if (this.files[fvpk].renderer)
        {
            this.files[fvpk].renderer.config = this.configs[config_key].renderer;
        }

        console.log("Set config:", this.files[fvpk].config);
    }

    update_preferences(e)
    {
        console.log("UPDATING PREFERENCES");
        console.log(e);
        let config_string_raw = $(e.target).data("config");
        let type = $(e.target).data("type")
        let value = $(e.target).val();
        let reparse = $(e.target).data("reparse");
        console.log("REPARSE IS", reparse);

        if (type == "int")
            value = parseInt(value);


        let components = config_string_raw.split(".");
        console.log("FV.CONFIGS", this.configs);
        console.log("COMPONENTS", components);

        // TODO: This seems like it's a dumb way to do this.
        switch (components.length) {
            case 4:
                this.configs[components[0]][components[1]][components[2]][components[3]] = value;
                break;
            case 3:
                this.configs[components[0]][components[1]][components[2]] = value;
                break;
            case 2:
                this.configs[components[0]][components[1]] = value;
                break;
            case 1:
                this.configs[components[0]] = value;
                break;
        }

        // Mark if reparsing is needed
        if (reparse)
            this.files[this.active_fvpk].parse_bytes();

        // And now... idk rerender?
        console.log("Config change applied!");
        this.files[this.active_fvpk].render();
        console.log("EXITING UPDATE PREFERENCES FUNCTION");
    }

    play_board(e)
    {
        console.log("Other globs?");
        console.log(fv_default_domain, mode, user_test);
        console.log("Argle?", argle_bargle);
        let scale = 1;
        let base_w = 640;
        let base_h = 350;
        let filename = this.files[this.active_fvpk].filename;
        let board_number = this.files[this.active_fvpk].selected_board;
        if (board_number == null)
            this.files[this.active_fvpk].world.current_board

        let key = zfile_info.key;
        let live_url = "/file/play/"+key+"?player=zeta&mode=popout&scale=" + scale + "&live=1&world="+filename+"&start=" +board_number;
        window.open(live_url, "popout-"+key, "width="+(base_w * scale)+",height="+(base_h * scale)+",toolbar=0,menubar=0,location=0,status=0,scrollbars=0,resizable=1,left=0,top=0");
    }

    ingest_debug_data(e)
    {
        console.log("Ingesting");
        $("#debug-wrapper").html(`<textarea>${JSON.stringify(this.configs, null, 4)}</textarea>`);
    }
}

export function create_handler_for_file(fvpk, filename, bytes, meta)
{
    let components = filename.split(".");
    let ext = "." + components[components.length - 1].toUpperCase();

    switch (true) {
        case EXTENSIONS_ZZT.indexOf(ext) != -1:
            return new ZZT_Handler(fvpk, filename, bytes, meta);
        case EXTENSIONS_SZZT.indexOf(ext) != -1:
            return new SZZT_Handler(fvpk, filename, bytes, meta);
        case EXTENSIONS_IMAGE.indexOf(ext) != -1:
            return new Image_Handler(fvpk, filename, bytes, meta);
        case EXTENSIONS_HIGH_SCORE.indexOf(ext) != -1:
            return new ZZT_High_Score_Handler(fvpk, filename, bytes, meta);
        case EXTENSIONS_HIGH_SCORE_SZZT.indexOf(ext) != -1:
            return new SZZT_High_Score_Handler(fvpk, filename, bytes, meta);
        case EXTENSIONS_TEXT.indexOf(ext) != -1:
            return new Text_Handler(fvpk, filename, bytes, meta);
        case fvpk == "fvpk-overview":
            return new Overview_Handler(fvpk, filename, bytes, meta);
        case fvpk == "fvpk-local":
            return new Local_File_Uploader_Handler(fvpk, filename, bytes, meta);
        case fvpk == "fvpk-debug":
            return new Debug_Handler(fvpk, filename, bytes, meta);
        default:
            return new Unsupported_Handler(fvpk, filename, bytes, meta);
    };

}
