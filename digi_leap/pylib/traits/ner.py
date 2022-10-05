import json

from tqdm import tqdm

from . import pipeline
from ..db import db


def ner(args):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        cxn.canned_delete(cxn, "traits", trait_set=args.trait_set)

        nlp = pipeline.build_pipeline()

        records = db.canned_select(cxn, "ocr_text", ocr_set=args.ocr_set)

        for cons in tqdm(records):
            batch = []

            if len(cons["ocr_text"].split()) < args.word_threshold:
                continue

            doc = nlp(cons["cons_text"])  # .replace("\n", " "))

            traits = [e._.data for e in doc.ents]

            for trait in traits:
                batch.append(
                    {
                        "trait_set": args.trait_set,
                        "ocr_id": cons["ocr_id"],
                        "trait": trait["trait"],
                        "data": json.dumps(trait),
                    }
                )
            db.canned_insert(cxn, "traits", batch)

        db.update_run_finished(cxn, run_id)
