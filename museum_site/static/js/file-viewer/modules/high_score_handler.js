import { Handler } from "./handler.js";

export class ZZT_High_Score_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "ZZT High Score Handler";
        this.envelope_css_class = "high-score-list";
        this.scores = [];
        this.show_nameless = true; // Show scores without a name entered
        this.max_name_length = 50;
        this.dash_count = 34;
    }

    parse_bytes() {
        console.log("high score parse bytes");
        this.pos = 0;
        this.data = new DataView(this.bytes.buffer);

        while (this.pos < this.data.byteLength)
        {
            let score = {};
            score["length"] = this.read_Uint8();  // First byte = Length of name
            score["name_full"] = this.read_Ascii(this.max_name_length);  // Maximum length of raw name
            score["name"] = score["name_full"].slice(0, score["length"]);
            score["score"] = this.read_Int16();  // 2 bytes of score
            this.scores.push(score);
        }
    }

    generate_html() {
        console.log("High score html generation");
        let html = `<pre class="cp437">Score  Name\n`;
        html += `-----  ${"-".repeat(this.dash_count)}\n`;
        for (var idx in this.scores)
        {
            if ((this.scores[idx].name.length != 0 || this.show_nameless) && this.scores[idx].score != -1)
            {
                let padded = ("" + this.scores[idx].score).padStart(5, " ");
                html += `${padded}  ${this.scores[idx].name}\n`;
            }
        }
        html += "</pre>";

        let output = [{"target": this.envelope_id, "html": html}];
        return output;
    }
}

export class SZZT_High_Score_Handler extends ZZT_High_Score_Handler
{
    constructor(fvpk)
    {
        super(fvpk);
        this.name = "SZZT High Score Handler";
        this.max_name_length = 60;
        this.dash_count = 20;
    }
}
