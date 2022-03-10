"""Find taxon notations on herbarium specimen labels."""
# import pandas as pd
# from traiter.old.vocabulary import LOWEST, Vocabulary
#
# from digi_leap.parsers.base import Base
# from digi_leap.pylib import const, patterns
# from digi_leap.pylib.trait import Trait
#
# PLANT_FAMILIES = const.DATA_DIR / 'itis_plant_families.csv'
# PLANT_GENERA = const.DATA_DIR / 'itis_plant_genera.csv'
#
# VOCAB = Vocabulary(patterns.VOCAB)
# VOCAB.part('word', r' \S+ ', capture=False, priority=LOWEST)
#
# DATA = pd.read_csv(PLANT_FAMILIES, na_filter=False, dtype=str)
# VOCAB.term('plant_family', DATA['complete_name'].tolist())
#
# DATA = pd.read_csv(PLANT_GENERA, na_filter=False, dtype=str)
# VOCAB.term('plant_genus', DATA['complete_name'].tolist())
#
#
# def convert(token):
#     """Normalize a parsed taxon notation"""
#     return Trait(start=token.start, end=token.end, value=token.group['value'])
#
#
# PLANT_TAXON = Base(
#     name='plant_taxon',
#     rules=[
#         VOCAB['eol'],
#         VOCAB.producer(convert, f' (?P<value> plant_genus word+ ) ')])
#
# PLANT_FAMILY = Base(
#     name='plant_family',
#     rules=[VOCAB.producer(convert, f' (?P<value> plant_family ) ')])
