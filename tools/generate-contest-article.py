import csv
import os
import sys

from datetime import datetime

import django

from django.template.loader import render_to_string
from django.template.defaultfilters import dictsort, slugify

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "museum.settings")
django.setup()

from django.contrib.auth.models import User  # noqa: E402

from museum_site.models import *  # noqa: E402

BASE_TEMPLATE = "museum_site/subtemplate/blank-contest-overview.html"

RANKING_TABLE_FIELDS = ["rank", "score_avg", "filename", "title", "author", "company", "score1", "score2", "score3", "score4", "score5"]
# Unused fields: id,
DEFAULTS = {"rank": "?", "score_avg": "<i>N/A</i>", "filename": "?", "id": "", "title": "!! UNKNOWN TITLE !!", "author": "<i>Unknown</i>", "company": "", "score1": "", "score2": "", "score3": "", "score4": "", "score5": ""}


def main():
    """
        "official" scores means we have data (it... might be partial)
        "partial" means we're relying on the IF page for top 3 and have no real individual scores
    """
    #contest = Contest(title="Winter 1999 24 Hours of ZZT")
    to_build = [


        Contest(title="Test 24 Hours of ZZT", topic="TestTopic", when="1991-01-15", judges=["Arnold", "Betty", "Charles", "Dos", "E. Honda"], available_scores=["official", "dos"], has_judgment=True, src_csv_path="/home/drdos/projects/museum-of-zzt/tools/info.csv", contest_zfile_key="24hoz-spr1999"),
        # 1998
        Contest(title="Summer 1998 24 Hours of ZZT", topic="Night", when="1998-07-10", host="Mono", judges=["Creator", "Kev Vance", "xf"], available_scores=["partial", "dos", "if"], has_judgment=False, src_csv_path="/home/drdos/projects/museum-of-zzt/tools/master-24hoz-data/night.csv", contest_zfile_key="24hoz-sum1998"),
        #Contest(title="Winter 1998 24 Hours of ZZT", topic="History", when="1998-12-28", judges=["myth", "Skullie", "Lemmer", "emmzee"], available_scores=["partial", "dos", "if"], has_judgment=False, src_csv_path="/home/drdos/projects/museum-of-zzt/tools/master-24hoz-data/history.csv", contest_zfile_key="24hoz-win1998"),
        # 1999
        Contest(title="Spring 1999 24 Hours of ZZT", topic="Fear", when="1999-03-27", judges=["HM", "GChucky", "myth", "DarkMage"], available_scores=["partial", "dos", "if"], has_judgment=False, src_csv_path="/home/drdos/projects/museum-of-zzt/tools/master-24hoz-data/fear.csv", contest_zfile_key="24hoz-spr1999"),
        Contest(title="Summer 1999 24 Hours of ZZT", topic="Space", when="1999-06-25", judges=["Misteroo", "HM", "Lemmer", "Skullie", "Tseng"], available_scores=["official", "dos", "if"], has_judgment=True, src_csv_path="/home/drdos/projects/museum-of-zzt/tools/master-24hoz-data/space.csv", contest_zfile_key="24hoz-sum1999"),
        Contest(title="Autumn 1999 24 Hours of ZZT", topic="Fantasy", when="1999-09-24", judges=["Knightt", "GChucky", "Koopo", "Skullie", "Tseng"], available_scores=["official", "dos", "if"], has_judgment=True, src_csv_path="/home/drdos/projects/museum-of-zzt/tools/master-24hoz-data/fantasy.csv", contest_zfile_key="24hoz-aut1999"),
    ]

    for contest in to_build:
        print("Building contest article for", contest.title)
        contest.load_csv_data()

        # Build tables
        tables = contest.build_tables()

        # Final template context
        context = {
            "render_date": datetime.now(),
            "entries": sorted(contest.entries, key=lambda item: item.get("title", "").lower()),
            "path": contest.static_path,
            "judges": contest.judges,
            "tables": tables,
            "has_judgment": contest.has_judgment,
        }

        # Render everything to a WIP article file
        rendered = render_to_string(BASE_TEMPLATE, context)
        with open(os.path.join("/home/drdos/projects/museum-of-zzt/wip/", contest.output_filename), "w") as fh:
            fh.write(rendered)
        print("Wrote", contest.output_filename, "to wip article directory.")
    return True


class Contest():
    def __init__(self, title="?", topic="?", when="", host="", judges=[], available_scores=[], has_judgment=True, src_csv_path="", contest_zfile_key=""):
        self.entries = []
        self.title = title
        self.topic = topic
        self.when = when
        self.available_scores = available_scores  # [official/partial, dos, if] (tables to present)
        self.has_judgment = has_judgment  # If there's anything to display, score or commentary, from judges in individual entry overviews
        self.judges = judges
        self.host = host if host else judges[0]
        self.src_csv_path = src_csv_path
        self.contest_zfile_key = contest_zfile_key
        self.output_filename = "24hoz-{}.html".format(topic.lower())

    @property
    def static_path(self):
        return "articles/{}/24hoz-{}/".format(datetime.now().year, self.topic.lower())

    #####################################################
    @property
    def ranking_table_fields(self):
        fields = ["Rank", "Score_Avg", "Filename", "Title", "Author", "Company"]
        if "official" in self.available_scores:
            for n in range(1, len(self.judges)):
                fields.append("Score{}".format(n))
        else:
            fields.remove("Score_Avg")
        return fields

    @property
    def dos_table_fields(self):
        return ["Dos_Tier", "Dos_Rank", "Filename", "Title", "Author", "Company"]

    @property
    def if_table_fields(self):
        return ["If_Rank", "If_Avg", "Filename", "Title", "Author", "Company", "If_Herc", "If_Hydra"]

    #####################################################

    def build_tables(self):
        tables = {}
        #to_build = self.get_potential_tables()
        to_build = self.available_scores
        for k in to_build:
            tables[k] = self.build_table(k)
        return tables

    def build_table(self, key):
        print("\tBuilding table `{}`. ".format(key), end="")
        if key == "official":
            headings = self.ranking_table_fields
            rows = sorted(self.entries, key=lambda item: item.get("score_avg", ""))
            rows.reverse()
        elif key == "partial":
            headings = self.ranking_table_fields
            rows = sorted(self.entries, key=lambda item: item.get("title", "").lower())
        elif key == "dos":
            headings = self.dos_table_fields
            rows = sorted(self.entries, key=lambda item: int(item.get("dos_rank", "")))
        elif key == "if":
            headings = self.if_table_fields
            rows = sorted(self.entries, key=lambda item: int(item.get("if_rank", 0)) if item.get("if_rank") != "" else 99999)
        print("\tHeadings: {} ".format(", ".join(headings)), end="")
        print("\tRows: {}".format(len(rows)))
        wip = ""
        for h in headings:
            wip += "<th>{}</th>".format(hr_header_from_key(h))

        heading_html = "<tr title='Click to sort'>{}</tr>\n".format(wip)

        body = ""
        for r in rows:
            wip = ""
            for f in headings:  # These are field names also...
                f_key = f.lower()
                wip += self.build_table_cell(r.get(f_key, "default"), f_key, r.get("prefix", "ERROR"))
            row_html = "<tr>{}</tr>".format(wip)
            body += row_html + "\n"

        table = heading_html + body
        return table

    def build_table_cell(self, value, k, idx, *args,):
        CELL_FORMATTING = {
            "default": {"raw": "<td>{}</td>", "args": [value]},
            "filename": {"raw": "<td><a href='/file/view/{}/?file={}&board=0'>{}</a></td>", "args": [self.contest_zfile_key, value, value]},
            "title": {"raw": "<td><a href='#entry-{}'>{}</a></td>", "args": [idx, value]},
            "author": {"raw": "<td>{}</td>", "args": [make_links(value, "author")]},
            "company": {"raw": "<td>{}</td>", "args": [make_links(value, "company")]},
            "rank": {"raw": "<td class='rank rank-{}'>{}</td>", "args": [value, value]},
            "dos_rank": {"raw": "<td class='rank rank-{}'>{}</td>", "args": [value, value]},
            "if_rank": {"raw": "<td class='rank rank-{}'>{}</td>", "args": [value, value]},
            "dos_tier": {"raw": "<td class='c tier-{}' >{}</td>", "args": [value.lower(), value]},
            "score_avg": {"raw": "<td class='r score-{}'>{}</td>", "args": [value.split(".")[0], value]},
            "if_avg": {"raw": "<td class='r score-{}'>{}{}</td>", "args": [percent_to_scale(value), value, "%" if value else ""]},
            "if_herc": {"raw": "<td class='r score-{}'>{}{}</td>", "args": [percent_to_scale(value), value, "%" if value and value != "N/A" else ""]},
            "if_hydra": {"raw": "<td class='r score-{}'>{}{}</td>", "args": [percent_to_scale(value), value, "%" if value and value != "N/A" else ""]},
        }

        if k.startswith("score"):
            for n in range(1, 6):
                CELL_FORMATTING["score" + str(n)] = {"raw": "<td class='r score-{}'>{}</td>", "args": [value.split(".")[0], value]}

        defined_keys = list(CELL_FORMATTING.keys())
        if k not in defined_keys:
            k = "default"
        output = CELL_FORMATTING[k]["raw"].format(*CELL_FORMATTING[k]["args"])
        return output

    def load_csv_data(self):
        suffixes = {"1": "st", "2": "nd", "3": "rd", "21": "st", "22": "nd", "23": "rd", "31": "st", "32": "nd", "33": "rd"}  # Listen.
        with open(self.src_csv_path) as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                row["remarks"] = []
                for n in range(1, len(self.judges)):
                    row["remarks"].append({"score": row["score{}".format(n)], "comment": row["comment{}".format(n)]})

                # Set additional data
                if row.get("rank"):
                    row["rank_suffix"] = suffixes.get(row["rank"], "th")

                # Re-add linebreaks to descriptions? Ugh.
                row["dos_desc"] = row["dos_desc"].replace("  ", "\n\n")

                # Award medal to top 3
                row["medal"] = {"1": "🥇 ", "2": "🥈 ", "3": "🥉 "}.get(row["rank"], "")

                self.entries.append(row)
                print("\tDetected entry:", row["title"])
        # Sort by title
        self.entries = sorted(self.entries, key=lambda item: item.get("title", ""))


def get_ranking_table_row(row, idx):
    output = ""
    for k in RANKING_TABLE_FIELDS:
        if row.get(k):
            output += get_ranking_table_cell(row[k], k, idx)
        else:
            output += "<td>{}</td>".format(DEFAULTS[k])
    output = "<tr>" + output + "</tr>\n"
    return output


def hr_header_from_key(key):
    if key.startswith("Dos_"):
        return key[4:]
    if key.startswith("If_"):
        return key[3:]
    if key == "Score_Avg":
        return "Avg"
    elif key.startswith("Score"):
        return key[:5] + key[5:]
    return key


def percent_to_scale(value):
    # Adapt IF percentages to a 0-10 value
    if not value:
        return "?"
    try:
        output = int(value.split(".")[0]) // 10
    except ValueError:  # We're very overzealous in running this function actually
        return "?"
    return output

def make_links(value, kind):
    output = []
    all_kinds = value.split("/")
    for k in all_kinds:
        output.append("<a href='/file/browse/{}/{}'>{}</a>".format(kind, slugify(k), k))
    return ", ".join(output)


if __name__ == '__main__':
    main()
