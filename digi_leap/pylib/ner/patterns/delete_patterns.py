# import re
# from spacy import registry


UNUSED = """ CARDINAL DATE EVENT FAC GPE LANGUAGE LAW LOC MONEY NORP
    ORDINAL ORG PERCENT PRODUCT QUANTITY TIME WORK_OF_ART not_name """.split()

# ####################################################################################
# NOT_A_PERSON = "digi_leap.not_a_person.v1"


# @registry.misc(NOT_A_PERSON)
# def not_a_person(ent):
#     """Remove bad person entities."""
#     if re.match(r"^\d+$", ent.text):
#         return True
#     return False


# ####################################################################################
# DELETE_WHEN = {
#     "PERSON": NOT_A_PERSON,
# }
