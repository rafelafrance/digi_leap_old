"""Patterns for names."""
# import pandas as pd
# from traiter.old.vocabulary import Vocabulary
#
# from digi_leap.pylib import patterns
# from digi_leap.pylib.const import DATA_DIR
#
# NAME_CSV = DATA_DIR / 'name_parts.csv'
#
# SUFFIXES = 'filho ii iii jr sr'.split()
#
# VOCAB = Vocabulary(patterns.VOCAB)
#
#
# def build_name_parts():
#     """Build name patterns."""
#     df = pd.read_csv(NAME_CSV, na_filter=False, dtype=str)
#     VOCAB.term('name_part', df['name'].tolist(), capture=False)
#
#
# build_name_parts()
#
# VOCAB.term('suffix', SUFFIXES)
# VOCAB.term('initial', r'[[:alpha:]] (?! \s* \d+ )')
