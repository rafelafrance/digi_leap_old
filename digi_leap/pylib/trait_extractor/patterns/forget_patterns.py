"""Remove entities when they meet these criteria."""


def spacy_entities() -> list[str]:
    """Forget default entities that interfere with other parsing."""
    return """
        CARDINAL DATE EVENT FAC GPE LANGUAGE LAW LOC MONEY NORP ORDINAL ORG
        PERCENT PERSON PRODUCT QUANTITY TIME WORK_OF_ART""".split()


def all_entities() -> list[str]:
    """Forget traits that sub-entities that are not part of a larger entity."""
    forget = """ us_county us_state us_state_or_county time_units month name """.split()
    forget += spacy_entities()
    return forget
