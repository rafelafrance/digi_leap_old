import json

from tqdm import tqdm

from . import pipeline
from ..db import db


def ner(args):
    with db.connect(args.database) as cxn:
        run_id = db.insert_run(cxn, args)

        cxn.execute("delete from traits where trait_set = ?", (args.trait_set,))

        nlp = pipeline.build_pipeline()

        records = db.canned_select(cxn, "consensus", consensus_set=args.consensus_set)

        for cons in tqdm(records):
            batch = []

            if len(cons["consensus_text"].split()) < args.word_threshold:
                continue

            doc = nlp(cons["cons_text"])  # .replace("\n", " "))

            traits = [e._.data for e in doc.ents]

            for trait in traits:
                batch.append(
                    {
                        "trait_set": args.trait_set,
                        "consensus_id": cons["consensus_id"],
                        "trait": trait["trait"],
                        "data": json.dumps(trait),
                    }
                )
            db.canned_insert(cxn, "traits", batch)

        db.update_run_finished(cxn, run_id)
