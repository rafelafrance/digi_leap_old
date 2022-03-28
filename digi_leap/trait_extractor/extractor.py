"""Extract traits from consensus text in a database."""
from ..pylib import db
from .pipelines import extractor_pipeline


def extract(args):
    """Do the extractions."""
    nlp = extractor_pipeline.pipeline()

    for cons in db.select_consensus(args.dabase, args.cons_set, limit=args.limit):
        batch = []
        doc = nlp(cons["cons_text"])
        for trait in [e._.data for e in doc.ents]:
            batch.append(
                {
                    "trait_set": args.trait_set,
                    "cons_id": cons["cons_id"],
                    "trait": trait["trait"],
                    "value": trait[trait["trait"]],
                    "start": trait["start"],
                    "end": trait["end"],
                    "data": trait,
                }
            )
        db.insert_traits(args.dabase, batch)
