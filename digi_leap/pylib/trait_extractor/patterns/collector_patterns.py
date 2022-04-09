"""Find collector notations on herbarium specimen labels."""
import re

from spacy import registry
from traiter.actions import RejectMatch
from traiter.patterns.matcher_patterns import MatcherPatterns

from . import common_patterns


class Collector:
    """Constants for collector parsing."""

    conj = ["CCONJ", "ADP"]
    collector_no = r"^\w*\d+\w*$"
    number_label = """ number no no. num num. # """.split()


ON_COLLECTOR_MATCH = "digi_leap.collector.v1"


def build_collector_patterns():
    """Build patterns for collector traits."""
    return MatcherPatterns(
        "collector",
        on_match=ON_COLLECTOR_MATCH,
        decoder=common_patterns.get_common_patterns()
        | {
            ":": {"TEXT": {"REGEX": r"^[:._]+$"}},
            "and": {"POS": {"IN": Collector.conj}},
            "by": {"LOWER": {"IN": ["by"]}},
            "col_label": {"ENT_TYPE": "col_label"},
            "col_no": {"LOWER": {"REGEX": Collector.collector_no}},
            "no_label": {"LOWER": {"IN": Collector.number_label}},
            "noise": {"TEXT": {"REGEX": r"^[._]+$"}},
            "name": {"ENT_TYPE": "name"},
            "maybe": {"POS": "PROPN"},
        },
        patterns=[
            "col_label? by? :? name+ no_label? :? col_no",
            "col_label  by? :? name+ no_label? :? col_no?",
            "col_label? by? :? name+ and name+ no_label? :? col_no",
            "col_label  by? :? name+ and name+ no_label? :? col_no?",
            "col_label? by? :? name+ noise name+ no_label? col_no",
            "col_label  by? :? name+ noise name+ no_label? col_no?",
            "col_label? by? :? name+ and name+ and name+ no_label? :? col_no",
            "col_label  by? :? name+ and name+ and name+ no_label? :? col_no?",
            #
            "col_label  by? :? maybe+ and name+ no_label? col_no?",
        ],
    )


@registry.misc(ON_COLLECTOR_MATCH)
def on_collector_match(ent):
    """Enrich a collector match."""
    people = []

    # Get the names and numbers
    for token in ent:
        if token.lower_ in Collector.number_label:
            pass
        elif token._.cached_label == "col_label":
            pass
        elif token.pos_ == "PROPN":
            people.append(token.text)
        elif token.pos_ in Collector.conj:
            pass
        elif match := re.search(Collector.collector_no, token.text):
            col_no = match.group(0)
            ent._.data["collector_no"] = col_no

    # Fix names with noise in them. "_Wayne.. Hutchins" which will parse as
    # two names ["Wayne", "Hutchins"] should be one name "Wayne Hutchins".
    new = people[:1]
    for i in range(1, len(people)):
        prev = people[i - 1]
        curr = people[i]
        if len(prev.split()) == 1 and len(curr.split()) == 1:
            new.pop()
            new.append(f"{prev} {curr}")
        else:
            new.append(curr)

    # Clean up names
    people = [re.sub(r",", "", p) for p in new]
    people = [re.sub(r"\s\s+", " ", p) for p in people]

    # All that for nothing
    if not people:
        raise RejectMatch()

    # Format output
    ent._.data["collector"] = people if len(people) > 1 else people[0]
