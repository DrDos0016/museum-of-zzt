import argparse
from datetime import datetime
import os
import json

import requests
from bs4 import BeautifulSoup

from exceptions import URLError


SC_URL = "http://www.stripcreator.com/"
FONT_PATH = os.path.join("resources", "LiberationSans-Bold.ttf")
FONT_SIZE = 12
FONT_TITLE_SIZE = 16
FONT_META_SIZE = 12
TEXT_FG = "#000000"
TEXT_BG = "#FFFFFF"
NARRATION_BG = "#FFFF00"
SPACING = 2
BALLOON_BG = "#FFFFFF"
COMIC_BG = "#000000"
PANEL_TEXT_AREA = 111  # Width provided for text by default


def save_comic(account, id, details=False, obscenities=True):
    url = (SC_URL + "comics/{}/{}/").format(
        account,
        id
    )

    print("Acquiring", url)

    cookies = {"nsfw":1} if obscenities else {}
    r = requests.get(url, cookies=cookies)
    if r.status_code != 200:
        raise URLError("Could not read URL: {}".format(url))

    # Parse the comic's data
    html = BeautifulSoup(r.text, "html.parser")
    comic_info = parse_comic_from_html(html)
    comic_info["sc_id"] = id

    # Acquire needed images
    #acquire_comic_images(comic_info)

    # Create the comic
    #create_comic(comic_info)

    return True


def parse_comic_from_html(html):
    comic_info = {"panels": []}

    # Title, Author, and Date come from the header
    header = html.find("table", id="comicborder")
    comic_info["title"] = header.a.text
    comic_info["author"] = header.find_all("a")[1].text
    comic_info["date"] = datetime.strptime(
        header.find_all("b")[1].contents[-1],
        "%m-%d-%y"
    ).strftime("%Y-%m-%d")

    # Parse the comic itself
    panels = [
        html.find("td", id="panel1"),
        html.find("td", id="panel2"),
        html.find("td", id="panel3")
    ]

    panel_idx = 0
    for panel in panels:
        # Handle 1/2 panel comics
        if panel is None:
            break

        # Get panel info
        panel_info = {}

        # Background
        background = panel.attrs["background"]
        panel_info["background"] = background.replace(
            SC_URL, ""
        )

        # Narration
        narration = panel.find("span", id="nar{}".format(panel_idx + 1))
        if narration.text:
            panel_info["narration"] = narration.text

        # Dialog
        panel_info["dialog"] = {"left": {}, "right": {}}
        dialog_num = (panel_idx * 2) + 1
        dialog_left = panel.find("span", id="dialog{}".format(dialog_num))
        dialog_right = panel.find("span", id="dialog{}".format(dialog_num + 1))

        panel_info["dialog"]["left"]["text"] = dialog_left.text
        panel_info["dialog"]["right"]["text"] = dialog_right.text

        # Dialog type
        type_left = panel.find("img", id="dtail{}".format(dialog_num))
        type_right = panel.find("img", id="dtail{}".format(dialog_num + 1))

        # Convert to dialog/thought
        if "dialog" in type_left.attrs["src"]:
            type_left = "dialog"
        else:
            type_left = "thought"

        if "dialog" in type_right.attrs["src"]:
            type_right = "dialog"
        else:
            type_right = "thought"

        panel_info["dialog"]["left"]["type"] = type_left
        panel_info["dialog"]["right"]["type"] = type_right

        # Characters
        character_num = (panel_idx * 2) + 1
        character_left = panel.find(
            "img",
            id="char{}".format(character_num)
        )
        character_right = panel.find(
            "img",
            id="char{}".format(character_num + 1)
        )

        panel_info["characters"] = {}
        panel_info["characters"]["left"] = (
            character_left.attrs["src"].replace(SC_URL, "")
        )
        panel_info["characters"]["right"] = (
            character_right.attrs["src"].replace(SC_URL, "")
        )

        # Add panel_info to comic_info
        comic_info["panels"].append(panel_info)

        panel_idx += 1
    return comic_info


def main():

    save_comic(account, id, details, obscenities)
    return True

if __name__ == "__main__":
    main()
