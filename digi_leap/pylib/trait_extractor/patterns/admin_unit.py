"""Parse administrative unit notations."""
# from digi_leap.pylib.trait import Trait
# from digi_leap.parsers import us_counties, us_states
# from traiter.old.vocabulary import Vocabulary
# from digi_leap.parsers.base import Base
#
# VOCAB = Vocabulary(us_counties.VOCAB)
#
#
# def convert(token):
#     """Normalize a parsed date"""
#     trait = Trait(start=token.start, end=token.end)
#
#     if token.group.get('us_county'):
#         trait.us_county = token.group['us_county'].title()
#
#     if token.group.get('us_state'):
#         trait.us_state = us_states.normalize_state(token.group['us_state'])
#
#     return trait
#
#
# ADMIN_UNIT = Base(
#     name='us_county',
#     rules=[
#         VOCAB['eol'],
#         VOCAB.term('skip', r""" of the """.split()),
#         VOCAB.term('co_label', r""" co | coun[tc]y """, capture=False),
#         VOCAB.term('st_label', r"""
#             ( plants | flora ) \s* of """, capture=False),
#         VOCAB.term('other', r"""alluvial flood river plain """.split()),
#         VOCAB.part('nope', r""" [(] """),
#         VOCAB['word'],
#
#         VOCAB.producer(convert, ' us_state? eol? co_label comma? us_county '),
#         VOCAB.producer(convert, ' us_county co_label comma? us_state? '),
#         VOCAB.producer(convert, ' us_county comma? us_state '),
#         VOCAB.producer(convert, """
#             st_label us_state eol? co_label us_county """),
#         VOCAB.producer(convert, ' st_label eol? us_state '),
#         VOCAB.producer(convert, ' (?<! skip ) us_state (?! other | nope ) '),
#     ])
