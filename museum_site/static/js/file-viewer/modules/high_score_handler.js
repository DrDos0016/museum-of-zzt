import { Handler } from "./handler.js";

export class ZZT_High_Score_Handler extends Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "ZZT High Score Handler";
        this.envelope_css_class = "high-score-list";
        this.scores = [];
        this.max_name_length = 50;
        this.dash_count = 34;

        this.tabs = [
            {"name": "preferences", "text": "Prefs."},
        ];
        this.default_tab = "preferences";
    }

    static initial_config = {
        "display": {
            "show_hidden_scores": 0,
        },
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

    write_html() {
        console.log("High score html generation");
        let html = `<pre class="cp437">Score  Name\n`;
        html += `-----  ${"-".repeat(this.dash_count)}\n`;
        for (var idx in this.scores)
        {
            if ((this.scores[idx].name.length != 0 || this.config.display.show_hidden_scores) && this.scores[idx].score != -1)
            {
                let padded = ("" + this.scores[idx].score).padStart(5, " ");
                html += `${padded}  ${this.scores[idx].name}\n`;
            }
        }
        html += "</pre>";

        let targets = [
            {"target": this.envelope_id, "html": html},
            {"target": "#preferences", "html": this.get_preferences(),},

        ];
        this.write_targets(targets)
        this.display_tab(this.default_tab);
        return true;
    }

    get_preferences()
    {
        let output = "";
        let config_key = this.get_config_key_for_handler();

        output += `<div class="field-wrapper">
            <label for="">Hidden Scores:</label>
            <div class="field-value"><select data-config="${config_key}.display.show_hidden_scores" data-type="int">
                <option value=0${(this.config.display.show_hidden_scores == false) ? " selected" : ""}>Hide*</option>
                <option value=1${(this.config.display.show_hidden_scores == true) ? " selected" : ""}>Show</option>
            </select></div>
            <p class="field-help">Show high scores stored with no name entered.</p>
        </div>`;
        return output;
    }
}

export class SZZT_High_Score_Handler extends ZZT_High_Score_Handler
{
    constructor(fvpk, filename, bytes, meta)
    {
        super(fvpk, filename, bytes, meta);
        this.name = "SZZT High Score Handler";
        this.max_name_length = 60;
        this.dash_count = 20;
    }
}
