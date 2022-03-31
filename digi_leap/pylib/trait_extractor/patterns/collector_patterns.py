"""Find collector notations on herbarium specimen labels."""
from spacy import registry
from traiter.patterns.matcher_patterns import MatcherPatterns

from .. import terms


DECODER = terms.COMMON_PATTERNS | {
    "person": {"ENT_TYPE": "PERSON"},
    "by": {"LOWER": {"IN": ["by"]}},
    "col_label": {"LOWER": {"IN": ["collector", "collected", "coll", "col"]}},
    "no_label": {"LOWER": {"IN": ["number", "no", "num"]}},
    "col_no": {"LOWER": {"REGEX": r"^\w+$"}},
    "and": {"POS": {"IN": ["CCONJ"]}},
    # "and": {"LOWER": {"IN": ["and", ","]}},
}

COLLECTOR = MatcherPatterns(
    "collector",
    on_match="digi_leap.collector.v1",
    decoder=DECODER,
    patterns=[
        "person+ col_no",
        "person+ and person+ col_no",
        "person+ and person+ and person+ col_no",
    ],
)

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


@registry.misc(COLLECTOR.on_match)
def collector(ent):
    """Enrich an administrative unit match."""
    print(ent)
    for token in ent:
        print(f"{token=} {token._.cached_label=}")
    # state = [e.text.title() for e in ent.ents if e.label_ in A_STATE][0]
    # ent._.data["us_state"] = terms.REPLACE.get(state, state)


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
