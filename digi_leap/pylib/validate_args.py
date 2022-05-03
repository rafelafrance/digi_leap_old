import sys

from . import db


def validate_trait_set(database, trait_set):
    with db.connect(database) as cxn:
        rows = db.execute(cxn, "select distinct trait_set from traits")
        all_trait_sets = [r["trait_set"] for r in rows]

    if trait_set in all_trait_sets:
        return

    print(f"{trait_set} is not a valid trait set.")
    print("Valid trait sets are:")
    print(", ".join(all_trait_sets))
    sys.exit()


def validate_cons_set(database, cons_set):
    with db.connect(database) as cxn:
        rows = db.execute(cxn, "select distinct cons_set from cons")
        all_cons_sets = [r["cons_set"] for r in rows]

    if cons_set in all_cons_sets:
        return

    print(f"{cons_set} is not a valid consensus set.")
    print("Valid consensus sets are:")
    print(", ".join(all_cons_sets))
    sys.exit()


def validate_ocr_set(database, ocr_set):
    with db.connect(database) as cxn:
        rows = db.execute(cxn, "select distinct ocr_set from ocr")
        all_ocr_sets = [r["ocr_set"] for r in rows]

    if ocr_set in all_ocr_sets:
        return

    print(f"{ocr_set} is not a valid OCR set.")
    print("Valid OCR sets are:")
    print(", ".join(all_ocr_sets))
    sys.exit()
