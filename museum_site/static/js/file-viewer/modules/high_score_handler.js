import { Handler } from "./handler.js";

export class ZZT_High_Score_Handler extends Handler
{
    constructor()
    {
        super();
        this.name = "ZZT High Score Handler";
        this.scores = [];
        this.show_nameless = true; // Show scores without a name entered
        this.max_name_length = 50;
        this.dash_count = 34;
    }

    render(fvpk, bytes) {
        super.render(fvpk, bytes);

        $(".envelope.active").removeClass("active");
        let envelope_id = "#envelope-" + fvpk;
        if ($(envelope_id).length == 0)
            this.create_envelope(fvpk, "image");

        let envelope = $(envelope_id);

        let output = `<pre class="cp437 high-scores">Score  Name\n`;
        output += `-----  ${"-".repeat(this.dash_count)}\n`;
        for (var idx in this.scores)
        {
            if ((this.scores[idx].name.length != 0 || this.show_nameless) && this.scores[idx].score != -1)
            {
                let padded = ("" + this.scores[idx].score).padStart(5, " ");
                output += `${padded}  ${this.scores[idx].name}\n`;
            }
        }
        output += "</pre>";

        envelope.html(output);
        envelope.addClass("active");
    }

    parse_bytes(bytes) {
        this.pos = 0;
        this.bytes = bytes;
        this.data = new DataView(bytes.buffer);

        while (this.pos < this.data.byteLength)
        {
            let score = {};
            score["length"] = this.read_Uint8();  // First byte = Length of name
            score["name_full"] = this.read_Ascii(this.max_name_length);  // Maximum length of raw name
            score["name"] = score["name_full"].slice(0, score["length"]);
            score["score"] = this.read_Int16();  // 2 bytes of score
            this.scores.push(score);
        }

        this.parsed = true;
        console.log(this.scores);
    }
}

export class SZZT_High_Score_Handler extends ZZT_High_Score_Handler
{
    constructor()
    {
        super();
        this.name = "SZZT High Score Handler";
        this.max_name_length = 60;
        this.dash_count = 20;
    }
}
