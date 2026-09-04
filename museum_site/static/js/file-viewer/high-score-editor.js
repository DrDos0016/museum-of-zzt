"use strict";
import { ZZT_High_Score_Handler, SZZT_High_Score_Handler } from "./modules/high_score_handler.js";


function initialize()
{
    zzt_hs_handler = new ZZT_High_Score_Handler("NOFVPK", "", null, {});
    szzt_hs_handler = new SZZT_High_Score_Handler("NOFVPK", "", null, {});
}

function from_hse()
{
    console.log("This func is defined in high-score-editor.js");
}

$(document).ready(initialize);
