"""Delete traits when they match these criteria at correct point in the pipeline."""
from spacy.util import registry

SPACY_ENTS = """ CARDINAL DATE EVENT FAC GPE LANGUAGE LAW LOC MONEY NORP
    ORDINAL ORG PERCENT PRODUCT QUANTITY TIME WORK_OF_ART """.split()  # PERSON


PARTIAL_ENTS = """ us_county us_state us_state-us_county time_units
    month name plant_taxon col_label det_label job_label level """.split()

DELETE_WHEN = "digi_leap.delete_when.v1"


@registry.misc(DELETE_WHEN)
def delete_when(_):  # ent):
    """Delete traits that fail these criteria."""
    return False
