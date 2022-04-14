"""Extract traits from consensus text in a database."""
import json

from tqdm import tqdm

from . import pipeline
from .. import db


def extract(args):
    run_id = db.insert_run(args)

    db.create_traits_table(args.database)
    db.delete(args.database, "traits", trait_set=args.trait_set)

    nlp_extractor = pipeline.build_pipeline()

    records = db.select_consensus(args.database, args.cons_set, limit=args.limit)

    for cons in tqdm(records):
        batch = []

        extractor_doc = nlp_extractor(cons["cons_text"])

        traits = [e._.data for e in extractor_doc.ents]

        for trait in traits:
            batch.append(
                {
                    "trait_set": args.trait_set,
                    "cons_id": cons["cons_id"],
                    "trait": trait["trait"],
                    "data": json.dumps(trait),
                }
            )
        db.insert_traits(args.database, batch)

    db.update_run_finished(args.database, run_id)
