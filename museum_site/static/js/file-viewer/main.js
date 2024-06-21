"use strict";

import { File_Viewer, create_handler_for_file } from "./modules/file_viewer.js";
import { KEY } from "./modules/core.js";


function initialize()
{
    console.log("Initalizing! HTML Settings are: auto_load =", auto_load, "file_size =", file_size, "fv_default_domain=", fv_default_domain);

    fv.default_domain = fv_default_domain;
    // Add Overview
    fv.files["fvpk-overview"] = create_handler_for_file("fvpk-overview", "Overview", [], {"loaded": true, "parsed": false});

    // Determine what to auto load
    if (auto_load.indexOf("?") != -1)
    {
        let params = new URLSearchParams(auto_load.split("?", 2)[1]);
        if (params.has("file"))
        {
            //fv.auto_load_target_str = `.fv-content[data-filename='${params.get("file")}']`;
            fv.has_auto_load_target = true;
            fv.auto_load_filename = params.get("file");
            fv.auto_load_board = params.get("board");
        }
    }


    // Bind pre-bindables
    $("#file-load-submit").click(ingest_file);
    $("#file-list").on("click", ".board-list .board", (e) => { fv.board_title_click(e); });
    $("#file-list").on("click", ".fv-content", output_file);
    $("#tabs").on("click", "div", display_tab);

    $("#file-viewer").on("click", ".board-link", (e) => { fv.board_title_click(e); });
    $("#fv-main").on("mousemove", ".fv-canvas", canvas_mousemove);
    $("#fv-main").on("mouseout", ".fv-canvas", canvas_mouseout);
    $("#fv-main").on("click", ".fv-canvas", canvas_click);
    $("#fv-main").on("dblclick", ".fv-canvas", canvas_double_click);

    $("#stat-info").on("change", "select[name=stat-sort]", (e) => { fv.resort_stats(e); });
    $("#stat-info").on("change", "input[name=show-codeless]", (e) => { fv.resort_stats(e); });
    $("#stat-info").on("click", ".stat-link", (e) => { fv.stat_click(e); });

    $("#world-info").on("click", "input[name=code-search-button]", (e) => { fv.code_search(e); });

    // Keyboard Shortcuts
    $(window).keyup(function (e){
        let match;
        if ($("input[name=q]").is(":focus") || $("input[name=code-search]").is(":focus")) // Disable when using search UI
            return false;

        if (! e.shiftKey && (e.keyCode == KEY.NP_PLUS || e.keyCode == KEY.PLUS || e.keyCode == KEY.J)) // Next Board
        {
            // Need to iterate over these until a non-hidden one is found.
            if (match = $(".board.selected").nextAll(".board"))
                match[0].click();
        }
        else if (! e.shiftKey && (e.keyCode == KEY.NP_MINUS || e.keyCode == KEY.MINUS || e.keyCode == KEY.K)) // Previous Board
        {
            if (match = $(".board.selected").prevAll(".board"))
                match[0].click();
        }
        else if (e.keyCode == KEY.NP_UP) { $("a.board-link[data-direction=north]").click(); }
        else if (e.keyCode == KEY.NP_DOWN) { $("a.board-link[data-direction=south]").click(); }
        else if (e.keyCode == KEY.NP_RIGHT) { $("a.board-link[data-direction=east]").click(); }
        else if (e.keyCode == KEY.NP_LEFT) { $("a.board-link[data-direction=west]").click(); }
        else if (e.keyCode == KEY.NP_LEFT) { $("a.board-link[data-direction=west]").click(); }
        else if (e.keyCode == KEY.W) {$("#tabs div[data-shortcut='W'").click();}
        else if (e.keyCode == KEY.B) {$("#tabs div[data-shortcut='B'").click();}
        else if (e.keyCode == KEY.E) {$("#tabs div[data-shortcut='E'").click();}
        else if (e.keyCode == KEY.S) {$("#tabs div[data-shortcut='S'").click();}
        else if (e.keyCode == KEY.P) {$("#tabs div[data-shortcut='P'").click();}
    });


    if (auto_load)
    {
        if (file_size < fv.auto_load_max_size)
            fetch_zip_file(auto_load);
        else
            fetch_zipinfo(auto_load);
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
        for(let [filename, info] of Object.entries(zip.files))
        {
            //console.log(info);
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
    console.log("SETTING FILE BYTES FOR", fv.files[fvpk].filename);
    // Sets the bytes for a file in the file registry
    fv.files[fvpk].bytes = data;
}


function ingest_file()
{
    // Checks that a file is ready to be manually uploaded into the file registry
    if ($("input[name=file_load_widget]").val())
        ingest_file_from_upload();
}


function ingest_file_from_upload()
{
    // Adds a manually uploaded file into the file registry
    console.log("UPLOADING");
    const file = $("input[name=file_load_widget]")[0].files[0];
    var reader = new FileReader();
    reader.onload = function (e) {
        var byte_array = new Uint8Array(reader.result);
        console.log(byte_array);
        fv.add_file(file.name, byte_array, {"loaded": true, "parsed": false});
        fv.render_file_list_item(file.name);
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
    let tab_id = $(this).attr("name");
    $("#details div.active").removeClass("active");
    $("#tabs div").removeClass("active");
    $(this).addClass("active");
    $(`#${tab_id}`).addClass("active");
}

function canvas_mousemove(e)
{
    let fvpk = $(this).parent().parent().attr("id").replace("envelope-", "");
    let border_size = parseInt($(this).css("border-left-width").replace("px", "")); // Assumes equal border sizes
    var rect = this.getBoundingClientRect();
    var base_x = e.pageX - rect.left - document.querySelector("html").scrollLeft - border_size;
    var base_y = e.pageY - rect.top - document.querySelector("html").scrollTop - border_size;
    fv.files[fvpk].mousemove({"base_x": base_x, "base_y": base_y});
}

function canvas_mouseout(e)
{
    let fvpk = $(this).parent().parent().attr("id").replace("envelope-", "");
    fv.files[fvpk].mouseout();
}

function canvas_click(e)
{
    let fvpk = $(this).parent().parent().attr("id").replace("envelope-", "");
    let border_size = parseInt($(this).css("border-left-width").replace("px", "")); // Assumes equal border sizes
    var rect = this.getBoundingClientRect();
    var base_x = e.pageX - rect.left - document.querySelector("html").scrollLeft - border_size;
    var base_y = e.pageY - rect.top - document.querySelector("html").scrollTop - border_size;
    fv.files[fvpk].canvas_click({"base_x": base_x, "base_y": base_y});
}

function canvas_double_click(e)
{
    let fvpk = $(this).parent().parent().attr("id").replace("envelope-", "");
    let border_size = parseInt($(this).css("border-left-width").replace("px", "")); // Assumes equal border sizes
    var rect = this.getBoundingClientRect();
    var base_x = e.pageX - rect.left - document.querySelector("html").scrollLeft - border_size;
    var base_y = e.pageY - rect.top - document.querySelector("html").scrollTop - border_size;
    fv.files[fvpk].canvas_double_click({"base_x": base_x, "base_y": base_y});
}

let fv = new File_Viewer();
let zip = new JSZip();
$(document).ready(initialize);
