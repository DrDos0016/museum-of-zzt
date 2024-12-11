import { Handler } from "./handler.js";
import { Character_Set } from "./character_set.js";

export class Charset_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "Charset Handler";
        this.envelope_css_class = "charset";
        this.initial_content = `<div class="inner-envelope-wrapper"><canvas class="fv-canvas ega-black-bg" data-foo="BAR"></canvas></div>`;

        this.char_width = 8;
        this.char_height = 14;
        this.character_set = new Character_Set();
    }

    parse_bytes() {
        this.pos = 0;
        this.data = new DataView(this.bytes.buffer);
    }

    write_html() {

        let canvas = document.querySelector(`#envelope-${this.fvpk} .fv-canvas`);
        console.log(this.fvpk);
        canvas.setAttribute("width", (16 * this.char_width) + "px");
        canvas.setAttribute("height", (16 * this.char_height) + "px");
        this.ctx = canvas.getContext("2d");
        this.ctx.imageSmoothingEnabled = false;
        this.ctx.strokeStyle = "#00FF00";
        this.ctx.fillStyle = "#00000000";
        this.ctx.fillRect(0, 0, canvas.width, canvas.height);
        console.log(this.ctx);

        console.log(canvas.width, canvas.height, this.data.byteLength);
        this.ctx.fillStyle = "#FFFFFF";

        let x = 0; // Origin coords of character
        let y = 0;
        let ch = 0
        let x_offset = 0;
        let y_offset = 0;

        while (ch < 255) // Characters
        {
            console.log("CHAR", ch);
            x_offset = 0;
            y_offset = 0;

            if ((ch != 0) && (ch % 16 == 0))
            {
                y += this.char_height;
                x = 0;
            }

            // Rows
            for (let row_idx = 0; row_idx < this.char_height; row_idx++)
            {
                x_offset = 0;
                let row = this.read_Uint8();
                let bits = ("00000000" + row.toString(2)).slice(-8);
                console.log(bits, "raw row:", row.toString(2));

                // Columns
                for (let idx in bits)
                {
                    if (bits[idx] == "1")
                        this.ctx.fillRect(x + x_offset, y + y_offset, 1, 1);
                    x_offset += 1;
                }
                y_offset += 1;
            }
            x += this.char_width;
            ch++;
        }

        // Populate character set
        this.character_set.name = this.filename;
        this.character_set.path = "";
        this.character_set.loaded = true;
        this.character_set.tile_width = this.char_width;
        this.character_set.tile_height = this.char_height;
        this.character_set.image = document.querySelector(`#envelope-${this.fvpk} .fv-canvas`).toDataURL();
        return true;
    }
}
