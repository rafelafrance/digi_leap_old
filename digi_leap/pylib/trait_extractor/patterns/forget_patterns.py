"""Remove entities when they meet these criteria."""
# Forget traits were supposed to be parts of a larger trait
FORGET_SPACY = """
    CARDINAL DATE EVENT FAC GPE LANGUAGE LAW LOC MONEY NORP ORDINAL ORG
    PERCENT PERSON PRODUCT QUANTITY TIME WORK_OF_ART""".split()

FORGET = """ us_county us_state us_state_or_county time_units month""".split()
FORGET += FORGET_SPACY
