import collections
import html
import itertools
import json
import re
from datetime import datetime
from typing import NamedTuple

import jinja2

from ..db import db

COLOR_COUNT = 14
BACKGROUNDS = itertools.cycle([f"cc{i}" for i in range(COLOR_COUNT)])
BORDERS = itertools.cycle([f"bb{i}" for i in range(COLOR_COUNT)])

TITLE_SKIPS = ["start", "end", "trait"]
TRAIT_SKIPS = TITLE_SKIPS

Formatted = collections.namedtuple("Formatted", "label_id text traits")
Trait = collections.namedtuple("Trait", "label data")
SortableTrait = collections.namedtuple("SortableTrait", "label start trait")


def write(args):
    with db.connect(args.database) as cxn:
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("./digi_leap/pylib/trait_writer/templates"),
            autoescape=True,
        )

        classes = {}
        formatted = []

        all_traits = db.canned_select("traits", cxn, trait_set=args.trait_set)
        groups = itertools.groupby(all_traits, key=lambda t: [t["consensus_id"]])

        for _, rows in groups:
            rows = [dict(r) for r in rows]
            for row in rows:
                row["trait"] = json.loads(row["data"])
            rows = sorted(rows, key=lambda r: r["trait"]["start"])
            formatted.append(
                Formatted(
                    row["label_id"],
                    format_text(rows[0]["consensus_text"], rows, classes),
                    format_traits(rows, classes),
                )
            )

        template = env.get_template("html_template.html").render(
            now=datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M"),
            trait_set=args.trait_set,
            data=formatted,
        )

        with open(args.out_file, "w", encoding="utf_8") as html_file:
            html_file.write(template)
            html_file.close()


def format_text(text, rows, classes) -> str:
    frags = []
    prev = 0

    for row in rows:
        trait = row["trait"]
        start = trait["start"]
        end = trait["end"]

        if prev < start:
            frags.append(html.escape(text[prev:start]))

        label = get_label(trait)
        cls = get_class(label, classes)

        title = ", ".join(
            f"{k}:&nbsp;{v}" for k, v in trait.items() if k not in TITLE_SKIPS
        )

        frags.append(f'<span class="{cls}" title="{title}">')
        frags.append(html.escape(text[start:end]))
        frags.append("</span>")
        prev = end

    if len(text) > prev:
        frags.append(html.escape(text[prev:]))

    text = "".join(frags)
    text = re.sub(r"\n", "<br/>", text)

    return text


def format_traits(rows, classes) -> list[NamedTuple]:
    traits = []

    sortable = []
    for row in rows:
        trait = row["trait"]
        label = get_label(trait)
        sortable.append(SortableTrait(label, trait["start"], trait))

    sortable = sorted(sortable)

    for label, grouped in itertools.groupby(sortable, key=lambda x: x.label):
        cls = get_class(label, classes)
        label = f'<span class="{cls}">{label}</span>'
        trait_list = []
        for trait in grouped:
            trait_list.append(
                ", ".join(
                    f"{k}:&nbsp;{v}"
                    for k, v in trait.trait.items()
                    if k not in TRAIT_SKIPS
                )
            )

        traits.append(Trait(label, "<br/>".join(trait_list)))

    return traits


def get_label(trait):
    part = trait["part"] if trait.get("part") else ""
    subpart = trait["subpart"] if trait.get("subpart") else ""
    trait = trait["trait"] if trait["trait"] not in ("part", "subpart") else ""
    return " ".join([p for p in [part, subpart, trait] if p])


def get_class(label, classes):
    if label not in classes:
        classes[label] = next(BACKGROUNDS)
    return classes[label]
