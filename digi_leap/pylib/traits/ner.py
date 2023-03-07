import json

from tqdm import tqdm

from . import pipeline
from ..db import db


def ner(args):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        db.canned_delete(cxn, "traits", trait_set=args.trait_set)

        nlp = pipeline.build_pipeline()

    with db.connect(args.database) as cxn:
        records = db.canned_select(cxn, "ocr_texts", ocr_set=args.ocr_set)
        if args.limit:
            records = records[: args.limit]

    with db.connect(args.database) as cxn:
        for ocr_text in tqdm(records):
            words = ocr_text["ocr_text"].split()
            batch = []

            if len(words) < args.word_threshold:
                continue

            text = " ".join(words)
            doc = nlp(text)

            traits = [e._.data for e in doc.ents]

            for trait in traits:
                batch.append(
                    {
                        "trait_set": args.trait_set,
                        "ocr_id": ocr_text["ocr_id"],
                        "trait": trait["trait"],
                        "data": json.dumps(trait),
                    }
                )
            db.canned_insert(cxn, "traits", batch)

        db.update_run_finished(cxn, run_id)
