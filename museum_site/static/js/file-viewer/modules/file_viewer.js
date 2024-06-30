import { Handler } from "./handler.js";
import { Image_Handler } from "./image_handler.js";
import { Overview_Handler } from "./overview_handler.js";
import { Text_Handler } from "./text_handler.js";
import { Unsupported_Handler } from "./unsupported_handler.js";
import { ZZT_High_Score_Handler, SZZT_High_Score_Handler } from "./high_score_handler.js";
import { ZZT_Handler } from "./zzt_handler.js";

const EXTENSIONS_IMAGE = [".BMP", ".JPG", ".PNG"];
const EXTENSIONS_HIGH_SCORE = [".HI", ".MH"];
const EXTENSIONS_HIGH_SCORE_SZZT = [".HGS"];
const EXTENSIONS_TEXT = [".TXT", ".NFO", ".DAT", ".OBJ", ".DOC"];
const EXTENSIONS_ZZT = [".ZZT"];

export class File_Viewer
{
    auto_load_max_size = 2097152;  // Maximum size of a zip file to automatically parse its contents
    //auto_load_max_size = 0;  // Maximum size of a zip file to automatically parse its contents
    fvi_count = 1000;
    zip_file_path = "";
    files = {};
    default_domain = "localhost";
    active_fvpk = "fvpk-overview"; // The FVPK of the currently displayed file
    has_auto_load_target = false;
    auto_load_file_name = "Overview"; // Click overview by default

    add_file(filename, bytes, meta)
    {
        // Adds a file into the file registry
        let fvpk = "fvpk-" + this.fvi_count;
        this.files[fvpk] = create_handler_for_file(fvpk, filename, bytes, meta);
        if (this.has_auto_load_target && (filename == this.auto_load_filename))
        {
            this.files[fvpk].selected_board = this.auto_load_board;
            this.files[fvpk].auto_click = window.location.hash;
            console.log("HASH IS", window.location.hash);
        }
        this.fvi_count++;
        return fvpk;
    }

    render_file_list_item(fvpk)
    {
        // Writes a list litem to the page's file list section
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
        this.files[fvpk].render();
    }

    reparse_active_file_as_text()
    {
        console.log("Textifying?");
        let fvpk = this.files[this.active_fvpk].fvpk;
        let filename = this.files[this.active_fvpk].filename;
        let bytes = this.files[this.active_fvpk].bytes;
        let meta = this.files[this.active_fvpk].meta;

        console.log("Filename is", filename);

        console.log("Before", this.files[this.active_fvpk].name);
        this.files[fvpk] = new Text_Handler(fvpk, filename, bytes, meta);
        console.log("After", this.files[this.active_fvpk].name);
        this.files[fvpk].render();
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
        window.location.hash = "";
        let bn = $(e.currentTarget).data("board-number");
        this.board_change(bn);
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
        console.log("COORDS?", coords);
        this.files[this.active_fvpk].write_element_info(coords.x, coords.y)
    }

    async stat_match_click(e)
    {
        console.log("STAT MATCH CLICK", e)
        let coord_str = `#${$(e.target).data("x")},${$(e.target).data("y")}`;
        this.files[this.active_fvpk].auto_click = coord_str;
        await this.board_title_click(e);
        history.replaceState(undefined, undefined, coord_str);
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

}

export function create_handler_for_file(fvpk, filename, bytes, meta)
{
    let components = filename.split(".");
    let ext = "." + components[components.length - 1].toUpperCase();

    console.log("Creating handler for", filename);

    switch (true) {
        case EXTENSIONS_ZZT.indexOf(ext) != -1:
            return new ZZT_Handler(fvpk, filename, bytes, meta);
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
        default:
            return new Unsupported_Handler(fvpk, filename, bytes, meta);
    };

}
