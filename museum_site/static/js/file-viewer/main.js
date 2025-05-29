"use strict";

import { File_Viewer, create_handler_for_file } from "./modules/file_viewer.js";
import { CHARACTER_SETS, get_mouse_coordinates, KEY } from "./modules/core.js";


function initialize()
{
    console.log("Initalizing! HTML Settings are: auto_load =", auto_load, "file_size =", file_size, "fv_default_domain=", fv_default_domain);
    history.replaceState({"open_file": "Overview"}, "", document.location.href);

    fv.default_domain = fv_default_domain;

    if (mode == "standard")
    {
        // Add Overview
        fv.files["fvpk-overview"] = create_handler_for_file("fvpk-overview", "Overview", [], {"loaded": true, "parsed": false});
        //fv.files["fvpk-debug"] = create_handler_for_file("fvpk-debug", "Debugging Information", [], {"loaded": true, "parsed": false});
    }
    else if (mode == "local")
    {
        fv.files["fvpk-local"] = create_handler_for_file("fvpk-local", "Upload Local File", [], {"loaded": true, "parsed": false});
        fv.files["fvpk-local"].active_fvpk = "fvpk-local";
    }

    // Determine what to auto load
    initialize_autoload();

    // Bind pre-bindables
    $("#file-load-submit").click(ingest_file);
    $("#file-list").on("click", ".board-list .board", (e) => { fv.board_title_click(e); });
    $("#file-list").on("click", ".fv-content", output_file);
    $("#tabs").on("click", "div", display_tab);
    $("#file-list").on("click", ".stat-match", (e) => { fv.stat_match_click(e); });

    $("#file-viewer").on("click", ".board-link", (e) => { fv.board_title_click(e); });
    $("#fv-main").on("mousemove", ".fv-canvas", canvas_mousemove);
    $("#fv-main").on("mouseout", ".fv-canvas", canvas_mouseout);
    $("#fv-main").on("click", ".fv-canvas", canvas_click);
    $("#fv-main").on("dblclick", ".fv-canvas", canvas_double_click);

    $("#details").on("mouseover", ".coords", (e) => { fv.hover_stat_start(e); });
    $("#details").on("mouseout", ".coords", (e) => { fv.hover_stat_stop(e); });

    $("#stat-info").on("change", "select[name=stat-sort]", (e) => { fv.resort_stats(e); });
    $("#stat-info").on("change", "input[name=show-codeless]", (e) => { fv.resort_stats(e); });
    $("#stat-info").on("click", ".stat-link", (e) => { fv.stat_click(e); });
    $("#stat-info").on("mouseover", ".stat-link", (e) => { fv.hover_stat_start(e); });
    $("#stat-info").on("mouseout", ".stat-link", (e) => { fv.hover_stat_stop(e); });

    $("#world-info").on("click", "input[name=code-search-button]", (e) => { fv.code_search(e); });
    $("#world-info").on("click", "input[name=clear-search]", (e) => { fv.clear_search(e); });

    $("#board-info").on("click", "#play-board", (e) => { fv.play_board(e); });

    $("#preferences").on("change", ".field-value select", (e) => { fv.update_preferences(e); });

    $("#fv-main").on("click", "#debug-ingest-button", (e) => { fv.ingest_debug_data(e); });

    $("#details").on("click", ".reparse-file-button", (e) => {fv.reparse_file_as_text(e); });

    /* Local Files */
    $("#fv-main").on("click", "#file-load-submit", ingest_file);


    // Keyboard Shortcuts
    $(window).keyup(function (e){
        let match;
        if ($("input[name=q]").is(":focus") || $("input[name=code-search]").is(":focus")) // Disable when using search UI
            return false;

        let active_info = {"handler": fv.files[fv.active_fvpk].name, "filename": fv.files[fv.active_fvpk].filename, "ext": fv.files[fv.active_fvpk].ext};

        if (! e.shiftKey && (e.keyCode == KEY.NP_PLUS || e.keyCode == KEY.PLUS || e.keyCode == KEY.J)) // Next Board
        {
            // Need to iterate over these until a non-hidden one is found.
            if ((match = $(".board.selected").nextAll(".board")) && match.length != 0)
                match[0].click();
        }
        else if (! e.shiftKey && (e.keyCode == KEY.NP_MINUS || e.keyCode == KEY.MINUS || e.keyCode == KEY.K)) // Previous Board
        {
            if ((match = $(".board.selected").prevAll(".board")) && match.length != 0)
                match[0].click();
        }
        else if (e.shiftKey && (e.keyCode == KEY.NP_PLUS || e.keyCode == KEY.PLUS || e.keyCode == KEY.J)) // Next File
        {
            if ((match = $(".fv-content.selected").nextAll(".fv-content")) && match.length != 0)
                match[0].click();
        }
        else if (e.shiftKey && (e.keyCode == KEY.NP_MINUS || e.keyCode == KEY.MINUS || e.keyCode == KEY.K)) // Previous File
        {
            if ((match = $(".fv-content.selected").prevAll(".fv-content")) && match.length != 0)
                match[0].click();
        }
        else if (e.shiftKey && e.keyCode == KEY.B) // Toggle blinking
        {
            if (match = $("select[data-config$='renderer.appearance.show_high_intensity_backgrounds']"))
            {
                let current = parseInt(match.val());
                match.val((current == 1 ? 0 : 1));
                match.change();
            }
        }
        else if (active_info.handler == "Text Handler" && e.keyCode == KEY.E) {shortcut_toggle_encoding();}


        else if (e.keyCode == KEY.NP_UP) { $("a.board-link[data-direction=north]").click(); }
        else if (e.keyCode == KEY.NP_DOWN) { $("a.board-link[data-direction=south]").click(); }
        else if (e.keyCode == KEY.NP_RIGHT) { $("a.board-link[data-direction=east]").click(); }
        else if (e.keyCode == KEY.NP_LEFT) { $("a.board-link[data-direction=west]").click(); }
        else if (e.keyCode == KEY.NP_LEFT) { $("a.board-link[data-direction=west]").click(); }
        else if (e.keyCode == KEY.W) {$("#tabs div[data-shortcut='W']").click();}
        else if (e.keyCode == KEY.B) {$("#tabs div[data-shortcut='B']").click();}
        else if (e.keyCode == KEY.E) {$("#tabs div[data-shortcut='E']").click();}
        else if (e.keyCode == KEY.S) {$("#tabs div[data-shortcut='S']").click();}
        else if (e.keyCode == KEY.P) {$("#tabs div[data-shortcut='P']").click();}
        else if (e.keyCode == KEY.Z) {shortcut_toggle_zoom();}

        // DEBUG TODO
        else if (e.keyCode == KEY.C) {
            console.log(fv.configs);
            console.log(CHARACTER_SETS);
            //console.log(fv.files[fv.active_fvpk]);
        }
    });

    // History
    $(window).bind("popstate", function(e) {
        console.log("POPSTATE", history.state);

        if (history.state)
        {
            if (history.state.open_file != fv.files[fv.active_fvpk].filename)
            {
                //console.log("I need to change the current file to", history.state.open_file);
                $(`.fv-content[data-filename="${history.state.open_file}"]`).click();

            }

            if (history.state.board != fv.files[fv.active_fvpk].selected_board)
            {
                if (typeof history.state.board == "undefined") // Close File
                {
                    $(`.fv-content[data-fvpk=${fv.active_fvpk}] .board-list`).remove();
                    $(`.fv-content[data-fvpk=${fv.active_fvpk}]`).removeClass("selected");
                }
                else // Change board
                {
                    fv.board_change(history.state.board);
                }
            }
        }
    });


    console.log("AUTO LOAD?", auto_load);
    if (auto_load)
    {
        if (file_size < fv.auto_load_max_size)
        {
            console.log("Fetching Complete File");
            fetch_zip_file(auto_load);
        }
        else
        {
            console.log("Fetching Only Zipinfo due to file size");
            fetch_zipinfo(auto_load);
        }
    }

    if (mode == "local")
    {
        fv.display_file_list();
        $(`.fv-content[data-fvpk='fvpk-local']`).click();
    }

    //DEBUG_FUNC();
}


function fetch_zip_file(url)
{
    // Fetches the zipfile found at the provided URL. Subject to CORS so no fun remote-loading out of the box.
    console.log("Fetching url", url);
    fetch(url).then(response => response.arrayBuffer()).then(data => open_zip(data));
}


function open_zip(buffer)
{
    // Adds the contents of a zipfile into the file viewer, setting the bytes property for all files, then lists the files
    console.log("Opening Zip");
    zip.loadAsync(buffer).then(function (){
        fv.files["fvpk-overview"].zip_comment = (zip.comment) ? zip.comment : ""; // Store zip file's comment if one exists
        for(let [filename, info] of Object.entries(zip.files))
        {
            let fvpk = fv.add_file(filename, {}, {
                "loaded": true,
                "parsed": false,
                "zipinfo": {
                    "filename": info.filename, "date": info.date, "compression": "?", "dir": info.dir, "crc32": info._data.crc32,
                    "compressed_size": info._data.compressedSize, "decompressed_size": info._data.uncompressedSize,
                }
            });
            info.async("uint8array").then(data => {
                set_file_bytes(fvpk, data);
                if (fv.files[fvpk].filename == fv.auto_load_filename)
                    $(`.fv-content[data-filename='${fv.auto_load_filename}']`).click();
            });
        }
        fv.display_file_list();

        if (! fv.has_auto_load_target) // Default auto load
            $(`.fv-content[data-fvpk='fvpk-overview']`).click();
    });
}


function set_file_bytes(fvpk, data)
{
    // Sets the bytes for a file in the file registry
    fv.files[fvpk].bytes = data;

    // Copy them to the charset if needed? TODO: Don't like this being added here
    if (fv.files[fvpk].name == "Charset Handler")
        CHARACTER_SETS[fvpk].bytes = data.buffer;
}


function ingest_file()
{
    // Checks that a file is ready to be manually uploaded into the file registry
    if ($("input[name=file-load-widget]").val())
        ingest_file_from_upload();
}


function ingest_file_from_upload()
{
    // Adds a manually uploaded file into the file registry
    console.log("UPLOADING");
    const file = $("input[name=file-load-widget]")[0].files[0];
    var reader = new FileReader();
    reader.onload = function (e) {
        var byte_array = new Uint8Array(reader.result);
        console.log(byte_array);
        let fvpk = fv.add_file(file.name, byte_array, {"loaded": true, "parsed": false});
        fv.render_file_list_item(fvpk);
    };
    reader.readAsArrayBuffer(file);
}


function fetch_zipinfo(url)
{
    // Fetches the zipfile's info found at the provided URL.
    fv.zip_file_path = url;
    if (url.indexOf("/") == 0)
        url = url.slice(1);
    url = "/ajax/fetch-zip-info/?path=" + url;
    console.log("Fetch zipinfo", url);
    fetch(url).then(response => response.json()).then(data => ingest_file_list_from_zipfile(data));
}


function ingest_file_list_from_zipfile(data)
{
    // Adds a zipinfo's file list into the file registry. Does not set file's bytes property.
    for (var idx = 0; idx < data["items"].length; idx++)
    {
        fv.add_file(data["items"][idx].filename, null, {"loaded": false, "parsed": false})
    }
    fv.display_file_list();
    if (fv.auto_load_filename) // Auto load if needed
        $(`.fv-content[data-filename='${fv.auto_load_filename}']`).click();
    else
        $(`.fv-content[data-fvpk='fvpk-overview']`).click();
}


function fetch_file_from_zip(zipfile_path, requested_file, requested_fvpk)
{
    // Fetches a file contained in a zipfile
    if (zipfile_path.indexOf("/") == 0)
        zipfile_path = zipfile_path.slice(1);
    let url = "/ajax/fetch-zip-content/?path=" + zipfile_path + "&content=" + requested_file;
    console.log("Request -> ", url);
    fetch(url).then(response => response.arrayBuffer()).then(data => ingest_unloaded_file(data, requested_file, requested_fvpk));
}


function ingest_unloaded_file(data, requested_file, fvpk)
{
    // Sets the file registry's bytes for the file to {data}. Then parses + displays it.
    console.log("Ingested unloaded file: ", requested_file);
    var byte_array = new Uint8Array(data);
    fv.files[fvpk].bytes = byte_array;
    fv.files[fvpk].meta.loaded = true;
    fv.display_file(fvpk);
}


function output_file(e)
{
    // Called when clicking on a file in the registry to display. Will load/parse file as needed
    let requested_fvpk = e.target.dataset.fvpk;

    if (! requested_fvpk)
    {
        console.log("NO FVPK!");
        console.log(e.target);
        return false;
    }

    let requested_filename = e.target.dataset.filename;
    console.log("User Click on File:", requested_fvpk);

    if (e.target.classList.contains("selected"))
    {
        console.log("THIS FILE IS OPEN ALREADY!");
        e.target.classList.remove("selected");
        fv.files[requested_fvpk].deactivate_active_envelopes();
        $(`.fv-content[data-fvpk=${requested_fvpk}] .board-list`).remove();
        return false;
    }

    fv.active_fvpk = requested_fvpk;

    if (requested_fvpk == "fvpk-overview") // Give the overview handler a copy of the zip info
    {
        fv.files["fvpk-overview"].fv_files = fv.files;
    }

    if (! fv.files[requested_fvpk].meta.loaded)
    {
        console.log("Hang on, we need to load the bytes still");
        console.log(fv.zip_file_path, requested_filename);
        fetch_file_from_zip(fv.zip_file_path, requested_filename, requested_fvpk);
    }
    else
        fv.display_file(requested_fvpk);
}

function DEBUG_FUNC()
{
    console.log("DEBUG FUNC");
    console.log(fv);
    return true;
}

function run_fv_function(e)
{
    // Use pre-set func name if set
    let to_run = (e.data.func_name) ? e.data.func_name : $(this).data("fv_func");
    let params = (e.data.value) ? $(this).data(e.data.value) : null;
    console.log("FV FUNC TO RUN IS", to_run);

    // If the active file has the function, call from there
    if (typeof fv.files[fv.active_fvpk][to_run] === "function")
    {
        console.log("Running FV Function");
        fv.files[fv.active_fvpk][to_run]($(this).val());
    }
    else
    {
        console.log("Running uh upper function?");
        fv[to_run](params);
    }
}

function display_tab()
{
    if ($(this).hasClass("hidden"))
        return false;

    let tab_id = $(this).attr("name");
    $("#details div.active").removeClass("active");
    $("#tabs div").removeClass("active");
    $(this).addClass("active");
    $(`#${tab_id}`).addClass("active");
}

function canvas_mousemove(e)
{
    let fvpk = $(this).parent().parent().attr("id").replace("envelope-", "");
    let zoom = fv.files[fvpk].config.display.zoom;
    let canvas_element = this;
    let coords = get_mouse_coordinates(e, canvas_element, zoom);
    fv.files[fvpk].mousemove(coords);
}

function canvas_mouseout(e)
{
    let fvpk = $(this).parent().parent().attr("id").replace("envelope-", "");
    fv.files[fvpk].mouseout();
}

function canvas_click(e)
{
    let fvpk = $(this).parent().parent().attr("id").replace("envelope-", "");
    let zoom = fv.files[fvpk].config.display.zoom;
    let canvas_element = this;
    let coords = get_mouse_coordinates(e, canvas_element, zoom);
    fv.files[fvpk].canvas_click(coords);
}

function canvas_double_click(e)
{
    let fvpk = $(this).parent().parent().attr("id").replace("envelope-", "");
    let zoom = fv.files[fvpk].config.display.zoom;
    let canvas_element = this;
    let coords = get_mouse_coordinates(e, canvas_element, zoom);
    fv.files[fvpk].canvas_double_click(coords);
}

function initialize_autoload()
{
    if (auto_load.indexOf("?") != -1)
    {
        let params = new URLSearchParams(auto_load.split("?", 2)[1]);
        if (params.has("file"))
        {
            fv.has_auto_load_target = true;
            fv.auto_load_filename = params.get("file");
            fv.auto_load_board = params.get("board");
        }
    }
}

function shortcut_toggle_zoom()
{
    let current = $("select[data-config='zzt_handler.display.zoom']").val();
    let updated = (current == "1") ? "2" : "1";
    $("select[data-config='zzt_handler.display.zoom']").val(updated);
    $("select[data-config='zzt_handler.display.zoom']").change();
}

function shortcut_toggle_encoding()
{
    let current = $("select[data-config='text_handler.renderer.encoding']").val();
    let updated = (current == "ascii-mapping") ? "utf-8" : "ascii-mapping";
    $("select[data-config='text_handler.renderer.encoding']").val(updated);
    $("select[data-config='text_handler.renderer.encoding']").change();
}

let fv = new File_Viewer();
let zip = new JSZip();
$(document).ready(initialize);
