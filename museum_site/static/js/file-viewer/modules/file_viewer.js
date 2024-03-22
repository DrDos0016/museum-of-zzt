import { Handler } from "./handler.js";
import { Image_Handler } from "./image_handler.js";
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

    add_file(filename, bytes, meta)
    {
        console.log(filename);
        // Adds a file into the file registry
        let fvpk = "fvpk-" + this.fvi_count;
        this.files[fvpk] = {"pk": fvpk, "bytes": bytes, "meta": meta, "handler": null};
        this.files[fvpk].meta["filename"] = filename;
        this.fvi_count++;
        return fvpk;
    }

    render_file_list_item(fvpk)
    {
        // Writes a list litem to the page's file list section
        $("#file-list").append(
            `<li class="fv-content" data-fvpk="${fvpk}" data-filename="${this.files[fvpk].meta.filename}">${this.files[fvpk].meta.filename}</li>`
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

        if (this.files[fvpk].handler === null)
        {
            console.log("HANDLER FOR", fvpk, "is null");
            let handler_class = get_handler_for_file(this.files[fvpk]);
            console.log("CREATED HANDLER CLASS", handler_class.name);
            this.files[fvpk].handler = handler_class;
            DEBUG_VAR = this.files[fvpk].handler;
        }

        this.files[fvpk].handler.render(this.files[fvpk].bytes);
    }
}

function get_handler_for_file(file)
{
    console.log("Getting file handler for", file);
    let filename = file.meta.filename;
    let components = filename.split(".");
    let ext = "." + components[components.length - 1].toUpperCase();

    switch (true) {
        case [".BMP", ".JPG", ".PNG"].indexOf(ext) != -1:
            return new Image_Handler(file.pk);
        case [".HI", ".MH"].indexOf(ext) != -1:
            return new ZZT_High_Score_Handler(file.pk);
        case ".HGS":
            return new SZZT_High_Score_Handler(file.pk);
        default:
            return new Unsupported_Handler(file.pk);
    };

}
