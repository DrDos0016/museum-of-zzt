import { Handler } from "./handler.js";
import { ASCII } from "./core.js";

export class ZZT_High_Score_Handler extends Handler
{
    constructor()
    {
        super();
        this.name = "ZZT High Score Handler";
        this.scores = [];
    }

    render(fvpk, bytes) {
        super.render(fvpk, bytes);

        $(".envelope.active").removeClass("active");
        let envelope_id = "#envelope-" + fvpk;
        if ($(envelope_id).length == 0)
            this.create_envelope(fvpk, "image");

        let envelope = $(envelope_id);

        let output = `<pre class="cp437 high-scores">Score  Name\n`;
        output += `-----  ----------------------------------\n`;
        for (var idx in this.scores)
        {
            let padded = ("" + this.scores[idx].score).padStart(5, " ");
            output += `${padded}  ${this.scores[idx].name}\n`;
        }
        output += "</pre>";

        envelope.html(output);
        envelope.addClass("active");
    }

    parse_bytes(bytes) {
        console.log("High score bytes", bytes);


        let foo = String.fromCharCode.apply(null, bytes);
        console.log("BTOA", foo);

        let idx = 0;

        while (idx < bytes.length)
        {
            let score = {};
            // First byte = Length of name
            score["length"] = bytes[idx];
            idx++;

            // 50 bytes of raw name
            score["name_full"] = Array.from(bytes.slice(idx, idx+50)).map((x) => ASCII[x]).join("");
            idx += 50;

            score["name"] = score["name_full"].slice(0, score["length"]);

            // 2 bytes of score
            score["score"] = bytes[idx] + (bytes[idx + 1] * 256);
            idx += 2;

            this.scores.push(score);
        }
    }
}
