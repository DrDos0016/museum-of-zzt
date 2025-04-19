"use strict";
var TEMPLATES = {
    "schedule": [
        "Here's this week's stream schedule! Join us live at https://twitch.tv/worldsofzzt/",
        "https://twitch.tv/worldsofzzt/ Stream schedule for this week:",
        "Presenting our schedule for this week. Watch along with us at https://twitch.tv/worldsofzzt/",
        "Let's play some ZZT! Check our schedule for this week below, and watch the stream at https://twitch.tv/worldsofzzt/",
    ],
    "vod": [
        "Last TODO's stream of TODO",
        "Here's the VOD for TODO's stream of TODO!",
        "This TODO we played TODO! You can check out the VOD here:",
        "The VOD for our stream of TODO is now available at:",
        "In case you missed TODO's stream of TODO, you can watch the VOD here:",
        "The recently streamed TODO now has its VOD up:",
    ],
    "live": [
        "Going live now with a stream of TODO! Join us at https://twitch.tv/worldsofzzt/",
        "Now streaming at https://twitch.tv/worldsofzzt/ Join us as we explore TODO",
        "Stream is up now! Check out https://twitch.tv/worldsofzzt/ while we play TODO",
        "It's time to stream! We're playing TODO today. Watch along at https://twitch.tv/worldsofzzt/",
    ],
    "early-access-article":
    [
        "Now available for $5+ Patrons! TODO",
        "Newly available for $5+ Patrons! TODO",
    ],
    "new-article":
    [
        "Now available for all Museum of ZZT visitors: TODO",
        "New for all Museum of ZZT visitors: TODO",
    ],
    "project-update":
    [
        "Time for a project update! TODO",
        "A new project update is now available at TODO",
    ]
}

function apply_form_shortcut()
{
    let shortcut_key = $("#id_form_shortcut").val();
    if (shortcut_key == "N/A")
        return false;

    let date = new Date();
    let month_name = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"][date.getMonth()];
    let formal_month_name = month_name.slice(0, 1).toUpperCase() + month_name.slice(1);
    let month_padded = ("0" + (date.getMonth() + 1)).slice(-2);

    if (shortcut_key == "schedule")
    {
        $("#id_title").val(`Stream Schedule - ${formal_month_name} ${date.getDate()}`);
        set_accounts(["bluesky", "discord", "mastodon", "tumblr", "twitter"]);
        $("#id_discord_channel").val("announcements");
        set_discord_mentions([]);
        $("#id_hashtags").val("#stream schedule, #zzt");

        // Set attachment 1 to assumed schedule URL:
        let schedule_path = `/static/zap/media/${date.getFullYear()}/${month_padded}/sched-${month_name}${date.getDate()}.png`;
        $("#id_media_1").val(schedule_path);
        let offset = date.getDay() % TEMPLATES.schedule.length;
        $("#id_body").val(TEMPLATES[shortcut_key][offset]);
    }
    else if (shortcut_key == "vod")
    {
        $("#id_title").val(`VOD: TODO`);
        set_accounts(["bluesky", "discord", "mastodon", "tumblr", "twitter"]);
        $("#id_discord_channel").val("announcements");
        set_discord_mentions([]);
        $("#id_hashtags").val("#vod, #zzt");

        let offset = date.getDay() % TEMPLATES.vod.length;
        $("#id_body").val(TEMPLATES[shortcut_key][offset]);
    }
    else if (shortcut_key == "live")
    {
        $("#id_title").val(`Now Streaming - TODO`);
        set_accounts(["bluesky", "discord", "mastodon", "tumblr", "twitter"]);
        $("#id_discord_channel").val("announcements");
        set_discord_mentions(["stream-alerts-dos", "stream-alerts-all"]);
        $("#id_hashtags").val("#streaming, #zzt");

        let offset = date.getDay() % TEMPLATES.live.length;
        $("#id_body").val(TEMPLATES[shortcut_key][offset]);
    }
    else if (shortcut_key == "early-access-article")
    {
        $("#id_title").val(`Patron Early Access - TODO`);
        set_accounts(["bluesky", "discord", "mastodon", "tumblr", "twitter"]);
        $("#id_discord_channel").val("announcements");
        let offset = date.getDay() % TEMPLATES["early-access-article"].length;
        $("#id_body").val(TEMPLATES[shortcut_key][offset]);
        $("#id_hashtags").val("#closer look, #early access, #zzt");
    }
    else if (shortcut_key == "new-article")
    {
        $("#id_title").val(`New Article - TODO`);
        set_accounts(["bluesky", "discord", "mastodon", "tumblr", "twitter"]);
        $("#id_discord_channel").val("announcements");
        let offset = date.getDay() % TEMPLATES["new-article"].length;
        $("#id_body").val(TEMPLATES[shortcut_key][offset]);
        $("#id_hashtags").val("#closer look, #zzt");
    }
    else if (shortcut_key == "project-update")
    {
        $("#id_title").val(`Project Update - ${formal_month_name} ${date.getDate()}`);
        set_accounts(["bluesky", "discord", "mastodon", "tumblr", "twitter"]);
        $("#id_discord_channel").val("announcements");
        let offset = date.getDay() % TEMPLATES["project-update"].length;
        $("#id_body").val(TEMPLATES[shortcut_key][offset]);
        $("#id_hashtags").val("#project update, #zzt");
    }
}

function set_accounts(account_list)
{
    $("input[name=accounts]:checked").click();
    for (let idx in account_list)
    {
        let account = account_list[idx];
        $("input[name=accounts][value=" + account + "]").click();
    }
}

function set_discord_mentions(role_list)
{
    let keys = {
        "stream-alerts-all": "838135077144625213",
        "stream-alerts-dos": "760545019273805834",
        "test-role": "1275156566643048449",

    }
    $("input[name=discord_mentions]:checked").click();
    for (let idx in role_list)
    {
        let role = keys[role_list[idx]];
        $("input[name=discord_mentions][value=" + role + "]").click();
    }
}
