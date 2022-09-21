import sys

from .db import db


def validate_trait_set(database, trait_set):
    with db.connect(database) as cxn:
        rows = db.select(cxn, "select distinct trait_set from traits", one_column=True)
        all_trait_sets = [r["trait_set"] for r in rows]

    if trait_set in all_trait_sets:
        return

    print(f"{trait_set} is not a valid trait set.")
    print("Valid trait sets are:")
    print(", ".join(all_trait_sets))
    sys.exit()


def validate_cons_set(database, consensus_set):
    with db.connect(database) as cxn:
        rows = db.select(
            cxn, "select distinct consensus_set from consensus", one_column=True
        )
        all_cons_sets = [r["consensus_set"] for r in rows]

    if consensus_set in all_cons_sets:
        return

    print(f"{consensus_set} is not a valid consensus set.")
    print("Valid consensus sets are:")
    print(", ".join(all_cons_sets))
    sys.exit()


def validate_ocr_set(database, ocr_set):
    with db.connect(database) as cxn:
        rows = db.select(cxn, "select distinct ocr_set from ocr_texts", one_column=True)
        all_ocr_sets = [r["ocr_set"] for r in rows]

    if ocr_set in all_ocr_sets:
        return

    print(f"{ocr_set} is not a valid OCR set.")
    print("Valid OCR sets are:")
    print(", ".join(all_ocr_sets))
    sys.exit()
