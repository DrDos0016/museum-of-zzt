"use strict";
import { Weave_CFG_Handler } from "./modules/weave_cfg_handler.js";


function initialize()
{
    console.log("INIT! W. CFG EDITOR")
    weave_cfg_handler = new Weave_CFG_Handler("NOFVPK", "", null, {});
}

function from_hse()
{
    console.log("This func is defined in weave-cfg-editor.js");
}

$(document).ready(initialize);
