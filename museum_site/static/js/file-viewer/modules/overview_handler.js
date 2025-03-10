import { Handler } from "./handler.js";
import { filesize_format } from "./core.js";

export class Overview_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Overview Handler";
        this.envelope_css_class = "overview";
        this.fv_files = {};
        this.preview_image_url = "";
        this.description = "";
        this.envelope_id = "#envelope-fvpk-overview";
        this.zip_comment = "";

        this.tabs = [
            {"name": "zip-info", "text": "Contents"},
        ];
        this.default_tab = "zip-info";
    }

    parse_bytes() {
        // Overview has no bytes, but this seems like a good place to pull data from the pre-rendered HTML
        this.preview_image_url = $("#fv-preview").attr("src");
        this.description = $("#envelope-fvpk-overview .zf-desc-wrapper").html();
        return false;
    }

    write_html() {
        let targets = [
            {"target": "#zip-info", "html": this.generate_zip_info_table()},
            {"target": this.envelope_id, "html": this.generate_overview()},
        ];

        this.write_targets(targets);
        this.display_tab(this.default_tab);
        return true;
    }

    generate_overview()
    {
        let desc = "";
        let TEMP_DISCLAIMER = "";
        if ((zfile_info.engine.indexOf("SZZT") != -1) || (zfile_info.engine.indexOf("WEAVE") != -1))
            TEMP_DISCLAIMER = `<div style='flex:1 0 100%;font-size:larger;' class="ega-red-bg"><p class="c">This file contains Weave ZZT or Super ZZT content which is currently unsupported!</p><p class="c"><a href="?new_to_old=1">View this file in the original file viewer</a></p></div>`;
        if (this.description)
            desc = `<div class="zf-desc-wrapper">${this.description}</div>`;
        let output = `
            ${TEMP_DISCLAIMER}
            <div class="zf-preview-wrapper"><img src="${this.preview_image_url}" class="image" id="fv-preview"></div>
            ${desc}
        `;
        return output;
    }

    generate_zip_info_table() {
        let output = "";
        let has_zipinfo = false;
        if (this.zip_comment)
            output += `<div>${this.zip_comment}</div>`;
        let zip_info_table = `
            <table class="zip-info-table">
            <tr><th>Filename</th><th>Mod. Date</th><th>CRC-32</th><th>Compressed Size</th><th>Decompressed Size</th></tr>
        `;
        // TODO: CRC32 is appearing as negative?
        for(let [key, file] of Object.entries(this.fv_files))
        {
            if (file.fvpk == "fvpk-overview" || file.fvpk == "fvpk-debug")
                continue;
            let zi = file.meta.zipinfo
            if (zi)
            {
                has_zipinfo = true;
                if (zi.dir)
                    continue;
                let fixed_crc = (zi.crc32 < 0) ? zi.crc32 + 4294967296 : zi.crc32; // IDK why the zip library uses a signed integer
                zip_info_table += `<tr>
                    <td>${file.filename}</td>
                    <td class="c">${zi.date.toISOString().replace("T", " ").slice(0, 19)}</td>
                    <td class="r">${fixed_crc}</td>
                    <td class="r" title="${zi.compressed_size} bytes">${filesize_format(zi.compressed_size)}</td>
                    <td class="r" title="${zi.decompressed_size} bytes">${filesize_format(zi.decompressed_size)}</td>
                </tr>`;
            }
        }

        if (has_zipinfo)
            output += zip_info_table;
        else
            output += `<i>Zipinfo is not available for large zip files.</i>`;

        output += `</table>`;
        return output;
    }
}
