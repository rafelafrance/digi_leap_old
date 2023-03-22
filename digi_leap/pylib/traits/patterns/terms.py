from plants.pylib.patterns import terms as p_terms
from traiter.pylib.patterns import terms as t_terms

# ##########################################################################
ADMIN_UNIT_TERMS = p_terms.ADMIN_UNIT_TERMS

REPLACE_ADMIN_UNITS = ADMIN_UNIT_TERMS.pattern_dict("replace")
COUNTY_IN = ADMIN_UNIT_TERMS.pattern_dict("inside")
POSTAL = ADMIN_UNIT_TERMS.pattern_dict("postal")

KEEP = """ admin_unit collector determiner """.split()
KEEP += t_terms.KEEP + p_terms.KEEP

# ##########################################################################
TREATMENT_TERMS = p_terms.PLANT_TERMS + t_terms.ALL_TERMS
