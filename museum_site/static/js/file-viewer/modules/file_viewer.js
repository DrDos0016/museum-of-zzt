import { Handler } from "./handler.js";
import { Image_Handler } from "./image_handler.js";
import { Text_Handler } from "./text_handler.js";
import { Unsupported_Handler } from "./unsupported_handler.js";
import { ZZT_High_Score_Handler, SZZT_High_Score_Handler } from "./high_score_handler.js";

export class File_Viewer
{
    auto_load_max_size = 2097152;  // Maximum size of a zip file to automatically parse its contents
    //auto_load_max_size = 0;  // Maximum size of a zip file to automatically parse its contents
    fvi_count = 1000;
    zip_file_path = "";
    files = {};
    default_domain = "localhost";
    active_fvpk = "fvpk-overview"; // The FVPK of the currently displayed file

    add_file(filename, bytes, meta)
    {
        // Adds a file into the file registry
        let fvpk = "fvpk-" + this.fvi_count;
        this.files[fvpk] = create_handler_for_file(fvpk, filename, bytes, meta);
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
    }

    display_file(fvpk)
    {
        // Displays the file {fvpk}
        console.log("FV wants to display...", fvpk);
        $(".fv-content.selected").removeClass("selected");
        $(".fv-content[data-fvpk=" + fvpk + "]").addClass("selected");
        this.files[fvpk].render();
    }

    reparse_active_file_as_text() {
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
}

function create_handler_for_file(fvpk, filename, bytes, meta)
{
    console.log("Creating a file handler for", filename);
    console.log("Meta btw is", meta);
    let components = filename.split(".");
    let ext = "." + components[components.length - 1].toUpperCase();

    switch (true) {
        case [".BMP", ".JPG", ".PNG"].indexOf(ext) != -1:
            return new Image_Handler(fvpk, filename, bytes, meta);
        case [".HI", ".MH"].indexOf(ext) != -1:
            return new ZZT_High_Score_Handler(fvpk, filename, bytes, meta);
        case ".HGS":
            return new SZZT_High_Score_Handler(fvpk, filename, bytes, meta);
        case [".TXT", ".NFO", ".DAT", ".OBJ"].indexOf(ext) != -1:
        return new Text_Handler(fvpk, filename, bytes, meta);
        default:
            return new Unsupported_Handler(fvpk, filename, bytes, meta);
    };

}