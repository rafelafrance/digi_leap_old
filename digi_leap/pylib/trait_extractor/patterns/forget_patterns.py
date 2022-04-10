"""Remove entities when they meet these criteria."""

SPACY_ENTITIES = """
        CARDINAL DATE EVENT FAC GPE LANGUAGE LAW LOC MONEY NORP ORDINAL ORG
        PERCENT PRODUCT QUANTITY TIME WORK_OF_ART""".split()  # PERSON

ALL_ENTITIES = """ us_county us_state us_state_or_county time_units month name
        plant_taxon col_label det_label job_label """.split()
ALL_ENTITIES += SPACY_ENTITIES
