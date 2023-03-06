import json
from collections import namedtuple

from ..db import db


TraitsInText = namedtuple("TraitsInText", "label_id text traits")


class TraitsInTextList:
    def __init__(self, text_traits):
        self.traits = [TraitsInText(t[0], t[1], t[2]) for t in text_traits]

    def __iter__(self):
        yield from self.traits


class LabelReader:
    def __init__(self, args):
        self.labels = self.read_traits(args.database, args.trait_set)

    @staticmethod
    def read_traits(database, trait_set):
        labels = []
        text = ""
        prev_label_id = -1
        label_id = -1
        traits = []

        with db.connect(database) as cxn:
            all_traits = db.canned_select(cxn, "traits", trait_set=trait_set)

        for trait in all_traits:
            if trait["label_id"] != prev_label_id:
                if label_id > -1:
                    labels.append((label_id, text, traits))

                text = trait["ocr_text"]
                label_id = trait["label_id"]
                traits = []
                prev_label_id = trait["label_id"]

            traits.append(json.loads(trait["data"]))

        if label_id > -1:
            labels.append((label_id, text, traits))

        return TraitsInTextList(labels)
