"""Extract traits from consensus text in a database."""
import json

from tqdm import tqdm

from .. import db
from .pipelines import extractor_pipeline
from .pipelines import vocab_pipeline


def extract(args):
    """Do the extractions."""
    run_id = db.insert_run(args)

    db.create_traits_table(args.database)
    db.delete(args.database, "traits", trait_set=args.trait_set)

    nlp_extractor = extractor_pipeline.build_pipeline()
    nlp_vocab = vocab_pipeline.build_pipeline()

    records = db.select_consensus(args.database, args.cons_set, limit=args.limit)

    for cons in tqdm(records):
        batch = []

        extractor_doc = nlp_extractor(cons["cons_text"])
        admin_unit_doc = nlp_vocab(cons["cons_text"])

        traits = [e._.data for e in extractor_doc.ents]
        traits += [e._.data for e in admin_unit_doc.ents]

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
