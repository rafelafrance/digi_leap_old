import itertools
import json

import spacy
from spacy.tokens import DocBin
from tqdm import tqdm

from . import tokenizer
from ..db import db


def prepare(args):
    doc_bin = DocBin()

    nlp = spacy.blank("en")
    tokenizer.setup_tokenizer(nlp)

    with db.connect(args.database) as cxn:
        all_traits = db.canned_select("traits", cxn, trait_set=args.trait_set)

    groups = itertools.groupby(all_traits, key=lambda t: [t["consensus_id"]])

    for cons_id, rows in tqdm(groups):
        rows = [dict(r) for r in rows]
        text = rows[0]["consensus_text"]
        doc = nlp(text)
        ents = []
        for row in rows:
            trait = json.loads(row["data"])
            span = doc.char_span(trait["start"], trait["end"], label=trait["trait"])
            ents.append(span)
        doc.ents = ents
        doc_bin.add(doc)

    doc_bin.to_disk(args.out_file)