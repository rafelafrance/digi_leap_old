#!/usr/bin/env python3
from digi_leap.pylib.ner import tokenizer

# python -m spacy train digi_leap/pylib/ner/config.cfg
# --output ./data/ner_models/
# --paths.train ./data/ner_models/traiter_2022-05-03.spacy
# --paths.dev ./data/ner_models/traiter_2022-05-03.spacy
# --gpu-id 0
# --code digi_leap/train_ner.py

if __name__ == "__main__":
    _ = tokenizer.TOKENIZER
