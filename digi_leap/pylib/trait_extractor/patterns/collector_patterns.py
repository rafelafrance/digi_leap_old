"""Find collector notations on herbarium specimen labels."""
import re

from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from ..terms import common_terms

CONJ = ["CCONJ"]
COL_NO = r"^\w*\d+\w*$"
COLL_LABEL = """ collector collected coll coll. col col. """.split()
NO_LABEL = """ number no no. num num. """.split()

DECODER = common_terms.COMMON_PATTERNS | {
    "person": {"ENT_TYPE": "PERSON"},
    "by": {"LOWER": {"IN": ["by"]}},
    "col_label": {"LOWER": {"IN": COLL_LABEL}},
    "no_label": {"LOWER": {"IN": NO_LABEL}},
    "col_no": {"LOWER": {"REGEX": COL_NO}},
    "and": {"POS": {"IN": CONJ}},
}

COLLECTOR = MatcherPatterns(
    "collector",
    on_match="digi_leap.collector.v1",
    decoder=DECODER,
    patterns=[
        "person+ col_no",
        "person+ and person+ col_no",
        "person+ and person+ and person+ col_no",
        "col_label person",
        "col_label person no_label? col_no",
    ],
)


@registry.misc(COLLECTOR.on_match)
def collector(ent):
    """Enrich an administrative unit match."""
    data = {}
    people = []
    for token in ent:
        if token._.cached_label == "PERSON":
            people.append(token.text)
        elif token.pos_ in CONJ:
            pass
        elif match := re.search(COL_NO, token.text):
            col_no = match.group(0)
            data["collector_no"] = col_no

    data["collector"] = people if len(people) > 1 else people[0]
    ent._.data = data

    # state = [e.text.title() for e in ent.ents if e.label_ in A_STATE][0]
    # ent._.data["us_state"] = terms.REPLACE.get(state, state)


#         VOCAB.term(
#             'part', r""" [[:alpha:]]+ """, priority=LOWEST, capture=False),
#
#         VOCAB.term('header_key', r' herbarium '.split()),
#
#         # With a label
#         VOCAB.producer(convert, """
#             (?<! other_label comma? name_part? ) (?<! part | col_no )
#                 noise? col_label comma? noise?
#                 (?P<col_name> collector
#                     ( joiner collector )* ( comma name_part )? )
#                 noise?
#             ( eol* ( (no_label? comma? (?P<collector_no> col_no )
#                 | no_label comma?
#                     (?P<collector_no> ( part | col_no ){1,2} ) ) ) )?
#                 """),
#
#         # Without a label
#         VOCAB.producer(convert, """
#             (?<= ^ | eol )
#             (?<! other_label noise? name_part? )  (?<! part | col_no )
#             noise? col_label? comma? noise?
#             (?P<col_name> initial? name_part+ ( joiner collector )* )
#             ( eol* ( (no_label? comma? (?P<collector_no> col_no )
#                 | no_label comma?
#                     (?P<collector_no> ( part | col_no ){1,2} ) ) ) )?
#             (?! header_key )
#             (?= month_name | col_no | eol | $ ) """),
#
#         VOCAB.producer(convert, """
#             (?P<col_name> collector ) (?P<collector_no> col_no)
#             """),
#     ])


# def convert(token):
#     """Build a collector trait"""
#     names = regex.split(
#         r'\s*(?:and|with|[,&])\s*',
#         token.group.get('col_name'))
#
#     traits = []
#
#     for name, suffix in zip_longest(names, names[1:], fillvalue=''):
#         name = regex.sub(r'\.{3,}.*', '', name)
#         if len(name) < MIN_LEN:
#             continue
#
#         trait = Trait(start=token.start, end=token.end)
#         trait.col_name = name
#
#         if suffix.lower() in name_parts.SUFFIXES:
#             trait.col_name = f'{name} {suffix}'
#
#         if name.lower() not in name_parts.SUFFIXES:
#             traits.append(trait)
#
#     if not traits:
#         return None
#
#     if token.group.get('collector_no'):
#         col_no = token.group['collector_no']
#         # Temp hack
#         if col_no[-1] in ('m', 'M'):
#             return None
#         traits[0].col_no = col_no
#
#     return squash(traits)
